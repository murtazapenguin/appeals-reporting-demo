"""
AI Processor Service for Document Processing and Medical Criteria Evaluation

NEW PIPELINE FLOW:
1. Filter documents by date range (90 days before service_date to denial_date)
2. OCR each document with caching (Azure OCR)
3. Document relevancy scoring with Gemini (fast initial scoring)
4. Shortlist top 3 documents
5. Detailed evidence extraction with Gemini Pro
6. Generate appeal letter with evidence and bounding boxes

Uses penguin-ai-sdk for all AI operations:
- OCR: Azure Document Intelligence
- Relevancy: Google Gemini Flash (fast, cheaper)
- Extraction/Appeals: Google Gemini Pro (accurate, detailed)
"""

import logging
import os
from json_repair import repair_json
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

# penguin-ai-sdk imports - ONLY these for AI operations
from penguin.ocr import AzureOCRProvider, ocr_line_to_bbox_format, strip_page_dimensions
from penguin.llm import create_client, UserMessage, SystemMessage

# MongoDB imports
from utils.db_utils import ocr_cache_collection, document_relevancy_collection, patient_documents_collection

# S3 imports
from utils.s3_storage import download_to_temp_file

# Configure logging with stdout handler
logger = logging.getLogger("ai_processor")
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

# Add handler if not already added (to avoid duplicate logs on reload)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class BoundingBox(BaseModel):
    """Bounding box coordinates in 8-point format (normalized 0-1)"""
    coords: List[float]  # [x1, y1, x2, y2, x3, y3, x4, y4]
    page: int


class Evidence(BaseModel):
    """Evidence extracted from document"""
    document_id: str
    document_name: str
    criterion_id: str
    criterion_question: str
    met: bool
    evidence_text: str
    page_number: int
    bbox: List[float]  # 8-point format
    explanation: str
    confidence: float = 1.0


class CriterionMatch(BaseModel):
    """Criterion match for relevancy scoring"""
    criterion_id: str
    relevant: bool = False
    confidence: float = 0.0


class DocumentRelevancy(BaseModel):
    """Document relevancy score from Gemini"""
    document_id: str
    document_name: str
    document_type: str = "other"
    relevancy_score: int  # Number of criteria this doc could support
    criteria_matches: List[CriterionMatch]


class DocumentProcessor:
    """
    Processes medical documents using Azure OCR, Gemini Flash for relevancy, and Gemini Pro for extraction.

    NEVER truncates OCR text - passes full text to LLM.
    """

    def __init__(self):
        """Initialize OCR and LLM providers."""
        # Azure OCR - Default provider
        self.ocr = AzureOCRProvider()
        logger.info("[INIT] Azure OCR provider initialized")

        # Initialize Gemini 3 Pro Preview for fast operations (relevancy scoring)
        self.gemini_flash = create_client("gemini", model="gemini-3-pro-preview")
        logger.info("[INIT] Gemini 3 Pro Preview initialized for fast LLM operations (relevancy scoring)")

        # Initialize Gemini 3 Pro Preview for detailed extraction and appeal generation
        self.gemini_pro = create_client("gemini", model="gemini-3-pro-preview")
        logger.info("[INIT] Gemini 3 Pro Preview initialized for evidence extraction and appeals")

    async def process_document_with_cache(self, file_path: str, document_id: str, patient_id: str) -> Dict:
        """
        Process a single document with OCR and cache the results.

        Args:
            file_path: Path to PDF file
            document_id: Unique document ID
            patient_id: Patient ID

        Returns:
            Dict with full_text, pages, and OCR lines with bounding boxes
        """
        # Check cache first
        cached = await ocr_cache_collection.find_one({"document_id": document_id})
        if cached:
            logger.info(f"[OCR CACHE] Using cached OCR for document {document_id}")
            return cached

        logger.info(f"[OCR] Starting OCR for document {document_id}")

        try:
            # OCR with Azure Document Intelligence
            ocr_result = await self.ocr.process_file(file_path)

            logger.info(f"[OCR] Completed for {document_id}, extracted {len(ocr_result.full_text)} characters")

            # Build line_index for fast line-number-to-bbox lookup (SDK v0.1.7+)
            # full_text now contains "content || line_number" format
            page_dims_list = ocr_result.metadata.get("page_dimensions", [])
            page_dims_map = {pd["page_number"]: pd for pd in page_dims_list}

            line_index = {}
            for line in ocr_result.lines:
                page_dims = page_dims_map.get(line.page_number, {"width": 8.5, "height": 11.0, "unit": "inch"})
                bbox_obj = ocr_line_to_bbox_format(line, os.path.basename(file_path), page_dims)
                stripped = strip_page_dimensions([bbox_obj])[0]
                # bbox is [[x1,y1,...,x4,y4]] — unwrap to flat 8-point list
                normalized_bbox = stripped["bbox"][0] if stripped.get("bbox") else [0, 0, 1, 0, 1, 1, 0, 1]
                line_index[str(line.line_number)] = {
                    "page_number": line.page_number,
                    "content": line.content,
                    "bbox": normalized_bbox
                }

            # Store OCR results
            ocr_data = {
                "document_id": document_id,
                "patient_id": patient_id,
                "file_path": file_path,
                "full_text": ocr_result.full_text,  # Now has "content || line_num" format from SDK v0.1.7
                "line_index": line_index,
                "pages": [
                    {
                        "page_number": page_num,
                        "text": "\n".join([
                            line.content for line in ocr_result.lines if line.page_number == page_num
                        ]),
                        "lines": [
                            {
                                "text": line.content,
                                "bbox": self._to_8point(line.bounding_box)
                            }
                            for line in ocr_result.lines if line.page_number == page_num
                        ]
                    }
                    for page_num in sorted(set(line.page_number for line in ocr_result.lines))
                ],
                "ocr_timestamp": datetime.utcnow()
            }

            # Cache in MongoDB
            await ocr_cache_collection.update_one(
                {"document_id": document_id},
                {"$set": ocr_data},
                upsert=True
            )

            logger.info(f"[OCR CACHE] Cached OCR for document {document_id}")

            return ocr_data

        except Exception as e:
            logger.error(f"[OCR ERROR] Failed for {document_id}: {str(e)}")
            raise

    async def score_document_relevancy(
        self,
        document: Dict,
        ocr_data: Dict,
        criteria: List[Dict]
    ) -> DocumentRelevancy:
        """
        Score document relevancy using Gemini.

        Args:
            document: Document metadata
            ocr_data: OCR results with full text
            criteria: List of criteria to evaluate

        Returns:
            DocumentRelevancy with score and criterion matches
        """
        document_id = document.get("_id") or document.get("document_id")
        document_name = document.get("document_name", "Unknown")

        logger.info(f"[RELEVANCY] Scoring document {document_name} against {len(criteria)} criteria")

        # Build prompt for Gemini
        criteria_list = "\n".join([
            f"{i+1}. [{c['id']}] {c['description']}"
            for i, c in enumerate(criteria)
        ])

        prompt = f"""
You are analyzing a medical document to determine which criteria it could potentially support.

**Document:** {document_name}
**Document Type:** {document.get('document_type', 'Unknown')}
**Document Date:** {document.get('document_date', 'Unknown')}

**Criteria to Evaluate:**
{criteria_list}

**Document Text (FULL TEXT):**
{ocr_data.get('full_text', '')}

**Instructions:**
1. For EACH criterion, determine if this document contains ANY information that could support it
2. Rate your confidence (0.0-1.0) for each criterion
3. Count how many criteria this document could potentially support

**Response Format (JSON):**
{{
    "relevancy_score": <number of criteria this doc could support>,
    "criteria_matches": [
        {{
            "criterion_id": "<criterion id>",
            "relevant": <true/false>,
            "confidence": <0.0-1.0>
        }}
    ]
}}

Return ONLY the JSON, no additional text.
"""

        try:
            # Call Gemini for fast relevancy scoring
            response = await self.gemini_flash.create(
                messages=[
                    SystemMessage("You are a medical document relevancy analyzer. Return only JSON."),
                    UserMessage(prompt)
                ],
                max_tokens=4096,
                temperature=0.0
            )

            # Parse JSON response
            result_text = response.content.strip()

            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()

            result = repair_json(result_text, return_objects=True)
            if not isinstance(result, dict):
                result = {}

            relevancy = DocumentRelevancy(
                document_id=document_id,
                document_name=document_name,
                document_type=document.get("document_type", "other"),
                relevancy_score=result.get("relevancy_score", 0),
                criteria_matches=[
                    CriterionMatch(**match) for match in result.get("criteria_matches", [])
                ]
            )

            logger.info(f"[RELEVANCY] Document {document_name} scored {relevancy.relevancy_score} criteria")

            # Cache relevancy score
            await document_relevancy_collection.update_one(
                {"document_id": document_id},
                {"$set": relevancy.dict()},
                upsert=True
            )

            return relevancy

        except Exception as e:
            logger.error(f"[RELEVANCY ERROR] Failed for {document_name}: {str(e)}")
            # Return low score on error
            return DocumentRelevancy(
                document_id=document_id,
                document_name=document_name,
                document_type=document.get("document_type", "other"),
                relevancy_score=0,
                criteria_matches=[]
            )

    async def extract_evidence_from_document(
        self,
        document: Dict,
        ocr_data: Dict,
        criteria: List[Dict]
    ) -> List[Evidence]:
        """
        Extract detailed evidence from a single document using Gemini Pro.

        Args:
            document: Document metadata
            ocr_data: OCR results with full text
            criteria: List of criteria to evaluate

        Returns:
            List of Evidence objects (2-3 per document)
        """
        document_id = document.get("_id") or document.get("document_id")
        document_name = document.get("document_name", "Unknown")

        logger.info(f"[EVIDENCE] Extracting evidence from {document_name}")

        # Build prompt for Claude
        criteria_list = "\n".join([
            f"{i+1}. [{c['id']}] {c['description']}"
            for i, c in enumerate(criteria)
        ])

        prompt = f"""
You are extracting medical evidence from a patient document.

**Document:** {document_name}
**Document Type:** {document.get('document_type', 'Unknown')}
**Document Date:** {document.get('document_date', 'Unknown')}

**Criteria to Evaluate:**
{criteria_list}

**Document Text (FULL TEXT — each line ends with || line_number):**
{ocr_data.get('full_text', '')}

**Instructions:**
1. Extract 2-3 KEY pieces of evidence from this document
2. For each evidence:
   - Identify which criterion it supports
   - Extract the EXACT text from the document
   - **Include the line_numbers where this evidence appears** (from the || markers at the end of each line)
   - Determine if the criterion is MET or NOT MET based on this evidence
   - Explain why this evidence supports or contradicts the criterion
3. Focus on the MOST IMPORTANT evidence that best supports the criteria

**Response Format (JSON):**
{{
    "evidences": [
        {{
            "criterion_id": "<criterion id>",
            "criterion_question": "<criterion question>",
            "met": <true/false>,
            "evidence_text": "<exact quote from document>",
            "line_numbers": [5, 6, 7],
            "explanation": "<why this meets/doesn't meet the criterion>"
        }}
    ]
}}

Return ONLY the JSON, no additional text. Limit to 2-3 evidence pieces.
"""

        try:
            # Call Gemini Pro for detailed evidence extraction
            response = await self.gemini_pro.create(
                messages=[
                    SystemMessage("You are a medical evidence extraction expert. Return only JSON."),
                    UserMessage(prompt)
                ],
                max_tokens=8192,
                temperature=0.0
            )

            # Parse JSON response
            result_text = response.content.strip()

            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()

            result = repair_json(result_text, return_objects=True)
            if not isinstance(result, dict):
                result = {}

            # Map evidence to bounding boxes
            evidence_list = []
            for evidence_data in result.get("evidences", [])[:3]:  # Limit to 3
                # Find bounding boxes — prefer line-number lookup (v0.1.7+), fallback to substring
                line_numbers = evidence_data.get("line_numbers", [])
                if line_numbers and "line_index" in ocr_data:
                    bboxes = self._find_evidence_bboxes_by_line(line_numbers, ocr_data)
                else:
                    bboxes = self._find_evidence_bboxes(
                        evidence_data.get("evidence_text", ""),
                        ocr_data
                    )

                # Create one evidence item per bbox (for multi-line evidence, this creates multiple highlights)
                for bbox in bboxes:
                    evidence = Evidence(
                        document_id=document_id,
                        document_name=document_name,
                        criterion_id=evidence_data.get("criterion_id", ""),
                        criterion_question=evidence_data.get("criterion_question", ""),
                        met=evidence_data.get("met", False),
                        evidence_text=evidence_data.get("evidence_text", ""),
                        page_number=bbox["page_number"],
                        bbox=bbox["bbox"],
                        explanation=evidence_data.get("explanation", ""),
                        confidence=0.9
                    )
                    evidence_list.append(evidence)

            logger.info(f"[EVIDENCE] Extracted {len(evidence_list)} pieces from {document_name}")

            return evidence_list

        except Exception as e:
            logger.error(f"[EVIDENCE ERROR] Failed for {document_name}: {str(e)}")
            return []

    async def evaluate_criteria(
        self,
        denial_id: str,
        denial_data: Dict,
        criteria: List[Dict],
        documents: List[Dict]
    ) -> Dict:
        """
        NEW PIPELINE: Evaluate medical necessity criteria against patient documents.

        Flow:
        1. Filter documents by date range
        2. OCR each document (with caching)
        3. Score document relevancy with Gemini
        4. Shortlist top 3 documents
        5. Extract detailed evidence with Gemini Pro
        6. Compile results

        Args:
            denial_id: Denial ID
            denial_data: Denial details (patient_id, service_date, etc.)
            criteria: List of criteria to evaluate
            documents: List of patient documents

        Returns:
            Evaluation results with evidence and bounding boxes
        """
        logger.info("=" * 60)
        logger.info(f"[PIPELINE] === STARTING CRITERIA EVALUATION ===")
        logger.info(f"[PIPELINE] Denial ID: {denial_id}")
        logger.info(f"[PIPELINE] Patient: {denial_data.get('patient_name')} ({denial_data.get('patient_id')})")
        logger.info(f"[PIPELINE] Procedure: CPT {denial_data.get('procedure_code')}")
        logger.info(f"[PIPELINE] Criteria count: {len(criteria)}")
        logger.info(f"[PIPELINE] Document count: {len(documents)}")
        logger.info("=" * 60)

        patient_id = denial_data.get("patient_id")

        # Step 1: Documents are already filtered by date range in the route
        logger.info(f"[STEP 1] Documents in date range:")
        for i, doc in enumerate(documents, 1):
            logger.info(f"  {i}. {doc.get('document_name')} ({doc.get('document_type')}) - {doc.get('document_date')}")

        # Step 2: OCR each document with caching
        logger.info(f"[STEP 2] Starting OCR for {len(documents)} documents...")
        ocr_results = {}
        for doc in documents:
            doc_id = str(doc.get("_id")) if doc.get("_id") else doc.get("document_id")
            file_path = doc.get("file_path")
            s3_key = doc.get("s3_key")
            doc_name = doc.get("document_name", "Unknown")
            temp_file = None

            try:
                # Try S3 first, then local file
                if s3_key:
                    logger.info(f"[OCR] Downloading from S3: {doc_name}")
                    temp_file = await download_to_temp_file(s3_key)
                    file_path = temp_file

                if file_path:
                    logger.info(f"[OCR] Processing: {doc_name}")
                    ocr_data = await self.process_document_with_cache(
                        file_path=file_path,
                        document_id=doc_id,
                        patient_id=patient_id
                    )
                    ocr_results[doc_id] = ocr_data
                    text_len = len(ocr_data.get("full_text", ""))
                    logger.info(f"[OCR] ✓ {doc_name}: {text_len} chars extracted")
                else:
                    logger.warning(f"[OCR] ✗ {doc_name}: No file_path or s3_key")
            except Exception as e:
                logger.error(f"[OCR] ✗ {doc_name}: FAILED - {str(e)}")
            finally:
                # Clean up temp file
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass

        logger.info(f"[STEP 2] OCR completed: {len(ocr_results)}/{len(documents)} documents processed")

        # Step 3: Group documents by type and only score when needed
        # If a type has only 1 document, include it directly (no LLM call needed)
        # If a type has multiple documents, score them to pick the best one
        docs_with_ocr = []
        for doc in documents:
            doc_id = str(doc.get("_id")) if doc.get("_id") else doc.get("document_id")
            if doc_id in ocr_results:
                docs_with_ocr.append(doc)

        # Group by document_type
        docs_by_type = {}
        for doc in docs_with_ocr:
            doc_type = doc.get("document_type", "other")
            if doc_type not in docs_by_type:
                docs_by_type[doc_type] = []
            docs_by_type[doc_type].append(doc)

        logger.info(f"[STEP 3] Document types: {', '.join(f'{t} ({len(d)})' for t, d in docs_by_type.items())}")

        top_documents = []
        for doc_type, type_docs in docs_by_type.items():
            if len(type_docs) == 1:
                # Only 1 doc of this type — include directly, no scoring needed
                doc = type_docs[0]
                doc_id = str(doc.get("_id")) if doc.get("_id") else doc.get("document_id")
                doc_name = doc.get("document_name", "Unknown")
                logger.info(f"[STEP 3] {doc_type}: 1 doc ({doc_name}) — skipping scoring")
                top_documents.append(DocumentRelevancy(
                    document_id=doc_id,
                    document_name=doc_name,
                    document_type=doc_type,
                    relevancy_score=0,
                    criteria_matches=[]
                ))
            else:
                # Multiple docs of same type — score to pick the best
                logger.info(f"[STEP 3] {doc_type}: {len(type_docs)} docs — scoring to pick best...")
                best_score = None
                for doc in type_docs:
                    doc_id = str(doc.get("_id")) if doc.get("_id") else doc.get("document_id")
                    doc_name = doc.get("document_name", "Unknown")
                    logger.info(f"[RELEVANCY] Scoring: {doc_name}")
                    relevancy = await self.score_document_relevancy(
                        document=doc,
                        ocr_data=ocr_results[doc_id],
                        criteria=criteria
                    )
                    logger.info(f"[RELEVANCY] ✓ {doc_name}: score={relevancy.relevancy_score}/{len(criteria)} criteria")
                    if best_score is None or relevancy.relevancy_score > best_score.relevancy_score:
                        best_score = relevancy
                top_documents.append(best_score)
                logger.info(f"[SHORTLIST] {doc_type}: picked best of {len(type_docs)} docs (score={best_score.relevancy_score})")

        logger.info("=" * 40)
        logger.info(f"[STEP 3] SELECTED DOCUMENTS ({len(top_documents)} total, 1 per type):")
        for i, doc in enumerate(top_documents, 1):
            logger.info(f"  ★ {i}. {doc.document_name} [{doc.document_type}]")
        logger.info("=" * 40)

        # Step 4: Extract detailed evidence from selected documents
        logger.info(f"[STEP 4] Extracting evidence from {len(top_documents)} documents...")
        all_evidence = []
        for relevancy in top_documents:
            # Find the original document
            doc = next((d for d in documents if str(d.get("_id", d.get("document_id"))) == relevancy.document_id), None)
            if doc and relevancy.document_id in ocr_results:
                logger.info(f"[EVIDENCE] Extracting from: {relevancy.document_name}")
                evidence_list = await self.extract_evidence_from_document(
                    document=doc,
                    ocr_data=ocr_results[relevancy.document_id],
                    criteria=criteria
                )
                logger.info(f"[EVIDENCE] ✓ {relevancy.document_name}: {len(evidence_list)} evidence pieces found")
                # Log unique evidence (deduplicate across bboxes)
                seen = set()
                for ev in evidence_list:
                    key = (ev.criterion_id, ev.evidence_text)
                    if key not in seen:
                        seen.add(key)
                        logger.info(f"    - {ev.criterion_id}: {'MET' if ev.met else 'NOT MET'} - \"{ev.evidence_text[:50]}...\"")
                all_evidence.extend(evidence_list)

        logger.info(f"[STEP 5] Total evidence extracted: {len(all_evidence)} pieces")

        # Step 6: Compile results by criterion
        results = []
        for criterion in criteria:
            criterion_id = criterion["id"]

            # Find all evidence for this criterion
            criterion_evidence = [e for e in all_evidence if e.criterion_id == criterion_id]

            # Determine if criterion is met (any evidence says it's met)
            met = any(e.met for e in criterion_evidence)

            # Format evidence
            evidence_list = [
                {
                    "document_id": e.document_id,
                    "document_name": e.document_name,
                    "page": e.page_number,
                    "text": e.evidence_text,
                    "bbox": e.bbox,
                    "confidence": e.confidence
                }
                for e in criterion_evidence
            ]

            # Explanation
            if criterion_evidence:
                explanation = "; ".join([e.explanation for e in criterion_evidence])
            else:
                explanation = "No evidence found in the top 3 most relevant documents"

            results.append({
                "id": criterion_id,
                "description": criterion["description"],
                "met": met,
                "evidence": evidence_list,
                "missing_documents": None if met else "Evidence not found or insufficient",
                "explanation": explanation
            })

        # Calculate win probability
        criteria_met = sum(1 for r in results if r['met'])
        total_criteria = len(criteria)
        win_probability = int((criteria_met / total_criteria) * 100) if total_criteria > 0 else 0

        logger.info("=" * 60)
        logger.info(f"[STEP 6] === EVALUATION COMPLETE ===")
        logger.info(f"[RESULT] Criteria met: {criteria_met}/{total_criteria}")
        logger.info(f"[RESULT] Win probability: {win_probability}%")
        for r in results:
            status = "✓ MET" if r['met'] else "✗ NOT MET"
            evidence_count = len(r.get('evidence', []))
            logger.info(f"  {r['id']}: {status} ({evidence_count} evidence pieces)")
        logger.info("=" * 60)

        return {
            "denial_id": denial_id,
            "total_criteria": total_criteria,
            "criteria_met": criteria_met,
            "win_probability": win_probability,
            "criteria": results,
            "top_documents": [
                {
                    "document_id": d.document_id,
                    "document_name": d.document_name,
                    "relevancy_score": d.relevancy_score
                }
                for d in top_documents
            ],
            "evaluated_at": datetime.utcnow()
        }

    def _find_evidence_bboxes_by_line(self, line_numbers: List[int], ocr_data: Dict) -> List[Dict]:
        """Look up bounding boxes by line number from cached OCR data (SDK v0.1.7+)."""
        bboxes = []
        line_index = ocr_data.get("line_index", {})

        for line_num in line_numbers:
            line_data = line_index.get(str(line_num))
            if line_data:
                bboxes.append({
                    "page_number": line_data["page_number"],
                    "bbox": line_data["bbox"]  # Already normalized 0-1
                })

        return bboxes

    def _find_evidence_bboxes(self, evidence_text: str, ocr_data: Dict) -> List[Dict]:
        """Find bounding boxes for evidence text in OCR data and normalize to 0-1 range."""
        bboxes = []

        # Clean evidence text for searching
        search_text = evidence_text.lower().strip()

        # Standard letter page dimensions in inches (Azure OCR returns inches)
        PAGE_WIDTH_INCHES = 8.5
        PAGE_HEIGHT_INCHES = 11.0

        # Search in each page
        for page in ocr_data.get("pages", []):
            page_number = page.get("page_number", 1)

            for line in page.get("lines", []):
                line_text = line.get("text", "").lower()

                # Simple substring match
                if search_text[:50] in line_text or line_text in search_text:
                    raw_bbox = line.get("bbox", [0, 0, 1, 0, 1, 1, 0, 1])

                    # Normalize bbox from inches to 0-1 range
                    # raw_bbox format: [x1, y1, x2, y2, x3, y3, x4, y4] in inches
                    normalized_bbox = [
                        raw_bbox[0] / PAGE_WIDTH_INCHES,   # x1
                        raw_bbox[1] / PAGE_HEIGHT_INCHES,  # y1
                        raw_bbox[2] / PAGE_WIDTH_INCHES,   # x2
                        raw_bbox[3] / PAGE_HEIGHT_INCHES,  # y2
                        raw_bbox[4] / PAGE_WIDTH_INCHES,   # x3
                        raw_bbox[5] / PAGE_HEIGHT_INCHES,  # y3
                        raw_bbox[6] / PAGE_WIDTH_INCHES,   # x4
                        raw_bbox[7] / PAGE_HEIGHT_INCHES,  # y4
                    ]

                    bboxes.append({
                        "page_number": page_number,
                        "bbox": normalized_bbox
                    })

        return bboxes

    async def generate_appeal_letter(
        self,
        denial_data: Dict,
        criteria_evaluation: Dict,
        documents: List[Dict]
    ) -> Dict:
        """
        Generate appeal letter using Gemini Pro with evidence from top documents ONLY.

        Args:
            denial_data: Denial information
            criteria_evaluation: Results from criteria evaluation
            documents: Patient documents (raw, without OCR text)

        Returns:
            Structured appeal letter with all sections
        """
        logger.info(f"[APPEAL] Generating letter for denial {denial_data.get('claim_number')}")

        # Get ONLY top documents that have evidence from evaluation
        top_doc_ids = [d["document_id"] for d in criteria_evaluation.get("top_documents", [])]
        logger.info(f"[APPEAL] Using only {len(top_doc_ids)} shortlisted documents with evidence")

        # Fetch OCR text from cache for ONLY the top documents
        top_documents_with_ocr = []
        for doc_id in top_doc_ids:
            # Get OCR cache for this document
            ocr_cache = await ocr_cache_collection.find_one({"document_id": doc_id})
            if ocr_cache:
                # Find original document metadata
                orig_doc = next((d for d in documents if str(d.get("_id", d.get("document_id"))) == doc_id), None)
                top_documents_with_ocr.append({
                    "document_name": orig_doc.get("document_name") if orig_doc else ocr_cache.get("document_id"),
                    "document_type": orig_doc.get("document_type", "Unknown") if orig_doc else "Unknown",
                    "document_date": orig_doc.get("document_date", "Unknown") if orig_doc else "Unknown",
                    "full_text": ocr_cache.get("full_text", "")  # OCR text from cache
                })
                logger.info(f"[APPEAL] Added OCR text for {top_documents_with_ocr[-1]['document_name']}")

        # Prepare context from ONLY the shortlisted documents with OCR
        document_context = self._prepare_document_context(top_documents_with_ocr)
        evidence_summary = self._prepare_evidence_summary(criteria_evaluation)

        # Fetch EOB document text separately (for denial code extraction in-prompt)
        eob_text = ""
        try:
            denial_id = str(denial_data.get("_id", denial_data.get("id", "")))
            eob_doc = await patient_documents_collection.find_one({
                "denial_id": denial_id,
                "document_type": "eob"
            })
            if eob_doc:
                eob_doc_id = str(eob_doc["_id"])
                eob_ocr = await ocr_cache_collection.find_one({"document_id": eob_doc_id})
                if eob_ocr:
                    eob_text = eob_ocr.get("full_text", "")
                    logger.info(f"[APPEAL] Found EOB document text ({len(eob_text)} chars)")
        except Exception as e:
            logger.warning(f"[APPEAL] Could not fetch EOB text: {e}")

        # Build prompt
        prompt = self._build_appeal_prompt(
            denial_data=denial_data,
            evidence_summary=evidence_summary,
            document_context=document_context,
            eob_text=eob_text
        )

        try:
            # Call Gemini Pro for letter generation
            response = await self.gemini_pro.create(
                messages=[
                    SystemMessage(
                        "You are a medical appeal letter writer. Generate professional, evidence-based appeal letters "
                        "following healthcare appeal standards. Include all 5 clinical justification subsections."
                    ),
                    UserMessage(prompt)
                ],
                max_tokens=8192,
                temperature=0.3
            )

            # Log sample of LLM response for debugging
            logger.info(f"[APPEAL] LLM response preview (first 500 chars): {response.content[:500]}")

            # Parse letter into structured sections
            letter = self._parse_appeal_letter(response.content, denial_data, criteria_evaluation)

            logger.info(f"[APPEAL] Letter generated with {len(letter['sections'])} sections")

            return letter

        except Exception as e:
            logger.error(f"[APPEAL ERROR] Failed to generate letter: {str(e)}")
            raise

    async def extract_denial_from_eob(
        self,
        document: Dict,
        ocr_data: Dict
    ) -> Optional[Dict]:
        """
        Extract denial code (e.g., CO-45) and narrative from EOB/Remittance Letter.

        Uses Bedrock Claude to parse denial information from OCR text.
        Returns dict with denial_code, denial_narrative, confidence, and line_numbers.
        """
        document_id = str(document.get("_id", document.get("document_id")))
        document_name = document.get("document_name", "Unknown")

        logger.info(f"[EXTRACTION] Starting denial extraction from EOB: {document_name}")

        full_text = ocr_data.get("full_text", "")
        if not full_text:
            logger.warning(f"[EXTRACTION] No OCR text available for document {document_id}")
            return None

        # Build extraction prompt
        prompt = f"""
You are analyzing an EOB (Explanation of Benefits) or Remittance Advice document.

Extract the PRIMARY denial code and denial narrative from this document.

**Document Text:**
{full_text}

**Instructions:**
- Extract the primary/overall denial code (e.g., CO-45, PR-96, OA-23)
- Extract the denial narrative/reason text that explains WHY the claim was denied
- Only extract information that is explicitly present in the document
- Do NOT fabricate or guess information
- If multiple denial codes exist, use the primary/most significant one

**Output Format (JSON):**
{{
    "denial_code": "CO-45",
    "denial_narrative": "Charges exceed fee schedule/maximum allowable or contracted/legislated fee arrangement",
    "confidence": 0.95
}}

Return ONLY the JSON object, no other text.
"""

        try:
            response = await self.gemini_pro.create(
                messages=[
                    SystemMessage("You are a medical claims document analyzer. Extract denial information accurately."),
                    UserMessage(prompt)
                ],
                max_tokens=1024,
                temperature=0.1
            )

            # Parse JSON response
            response_text = response.content.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            result = repair_json(response_text, return_objects=True)
            if not isinstance(result, dict):
                logger.warning(f"[EXTRACTION] Empty or invalid response for document {document_id}")
                return None

            # Validate extraction
            if not result.get("denial_code") and not result.get("denial_narrative"):
                logger.warning(f"[EXTRACTION] No denial information found in document {document_id}")
                return None

            # Add metadata
            result["extracted_from_document_id"] = document_id
            result["extracted_at"] = datetime.utcnow()
            result["extraction_confidence"] = result.get("confidence", 0.0)

            logger.info(f"[EXTRACTION] Successfully extracted denial info: code={result.get('denial_code')}, confidence={result.get('confidence')}")

            return result

        except Exception as e:
            logger.error(f"[EXTRACTION ERROR] Failed to extract denial info from {document_id}: {str(e)}")
            return None


    def _get_denial_code(self, denial_data: Dict) -> str:
        """Get denial code with fallback logic."""
        extraction = denial_data.get('denial_extraction', {})
        if extraction and extraction.get('denial_code') and extraction.get('extraction_confidence', 0) > 0.7:
            return extraction['denial_code']
        return denial_data.get('denial_code') or "Not specified"

    def _get_denial_narrative(self, denial_data: Dict) -> str:
        """Get denial narrative with fallback logic."""
        extraction = denial_data.get('denial_extraction', {})
        if extraction and extraction.get('denial_narrative') and extraction.get('extraction_confidence', 0) > 0.7:
            return extraction['denial_narrative']
        return denial_data.get('denial_reason') or "Not specified"

    def _get_provider_info(self, denial_data: Dict) -> Dict:
        """Get provider info from denial record database fields."""
        logger.info(f"[APPEAL] Using provider info from denial record")
        return {
            "name": denial_data.get('provider_name', 'Provider'),
            "address": denial_data.get('provider_address'),
            "phone": denial_data.get('provider_phone'),
            "npi": denial_data.get('provider_npi'),
            "tax_id": denial_data.get('provider_tax_id'),
            "practice_name": denial_data.get('provider_practice_name')
        }

    def _build_appeal_prompt(self, denial_data: Dict, evidence_summary: str, document_context: str, eob_text: str = "") -> str:
        """Build prompt for appeal letter generation. Includes raw EOB text so the LLM can extract denial codes and respond in one shot."""

        # Get denial info with extraction fallback
        denial_code = self._get_denial_code(denial_data)
        denial_narrative = self._get_denial_narrative(denial_data)

        # Build EOB section if we have the raw text
        eob_section = ""
        if eob_text:
            eob_section = f"""
**EOB / REMITTANCE ADVICE DOCUMENT (RAW TEXT):**
Read this EOB carefully. For each denied service line, identify the CPT code, denial code (e.g. CO-45), and the verbatim denial narrative. You MUST quote these exactly in the letter and respond to each one.

{eob_text}
"""

        prompt = f"""
You are writing a professional medical post-claim appeal letter. Follow the EXACT structure below.

**CLAIM INFORMATION:**
- Claim Number: {denial_data.get('claim_number')}
- Patient: {denial_data.get('patient_name')}
- DOB: {denial_data.get('patient_dob')}
- Provider: {denial_data.get('provider_name')}
- Payer: {denial_data.get('payer_name')}
- Service Date: {denial_data.get('service_date')}
- Denial Date: {denial_data.get('denial_date')}
- Denial Code: {denial_code}
- Denial Reason: {denial_narrative}
- CPT Code(s): {denial_data.get('procedure_code')}
- Diagnosis Codes: {denial_data.get('diagnosis_codes')}
- Claim Amount (Billed): ${denial_data.get('claim_amount', 0):.2f}
- Paid Amount: ${denial_data.get('paid_amount', 0):.2f}
- Denied Amount: ${denial_data.get('denied_amount', 0):.2f}
{eob_section}
**EVIDENCE FROM MEDICAL RECORDS:**
{evidence_summary}

**FULL DOCUMENT CONTEXT:**
{document_context}

**REQUIRED OUTPUT FORMAT (follow exactly):**

Dear Claims Review Team:

I am writing to formally appeal your denial of payment for the above-referenced claim dated {denial_data.get('denial_date')}.

DENIAL INFORMATION:
[Read the EOB/Remittance Advice document provided above. Quote the EXACT denial code(s) and denial narrative(s) from it. State how much was billed, paid, and denied.]

DENIED SERVICES:

[Create a properly formatted markdown table with this EXACT format:]

| CPT Code | Description | Billed | Paid | Denied | Denial Code | Denial Reason |
|----------|-------------|--------|------|--------|-------------|---------------|
| [code] | [description] | $[amount] | $[amount] | $[amount] | [code] | [verbatim reason from EOB] |

**Total Billed:** ${denial_data.get('claim_amount', 0):.2f}
**Total Paid:** ${denial_data.get('paid_amount', 0):.2f}
**Total Denied:** ${denial_data.get('denied_amount', 0):.2f}

ASSOCIATED DIAGNOSIS CODES:
[List all diagnosis codes with descriptions]

RESPONSE TO EACH SERVICE LINE DENIAL:

[For EACH denied service line listed above, write a targeted response:]

**CPT [code] - [procedure name]:**
The EOB states: "[Quote the EXACT denial code and narrative VERBATIM from the EOB document]"

Our Response: [Write 1-2 paragraphs refuting THIS specific denial reason with evidence from the medical records. Use specific dates, measurements, and clinical findings.]

[Repeat for every denied service line]

REASON FOR APPEAL (OVERALL):

[Write 1-2 paragraphs providing an overall summary of why the denial is incorrect, referencing the specific denial reasons quoted above.]

CLINICAL JUSTIFICATION:

1. Patient Clinical History and Conservative Treatment Failure

[Write 2-3 paragraphs describing:
- Patient demographics and presenting symptoms
- Duration and severity of symptoms
- ALL conservative treatments attempted with dates and durations
- Why each conservative treatment failed
- Impact on activities of daily living
Use specific evidence from the documents provided]

2. Diagnostic Imaging Findings

[Write 1-2 paragraphs describing:
- MRI/X-ray/CT findings with dates
- Specific pathology identified (tears, stenosis, fractures, etc.)
- Measurements and severity grading
- Correlation with clinical symptoms
Use exact findings from imaging reports in the documents]

3. Intraoperative Findings and Medical Necessity of Each CPT Code

[For EACH CPT code billed, write a separate paragraph:
CPT [code] ([procedure name]): [Describe what was found during surgery, why this specific procedure was necessary, and what pathology it addressed. Link to pre-op imaging and symptoms. Be very specific about findings.]

Use operative report details from the documents]

4. Adherence to Clinical Guidelines and Standards of Care

[Write 2-3 paragraphs describing:
- Relevant clinical guidelines (AAOS, NASS, etc.) that support this treatment
- Payer's own medical policy criteria and how patient meets them
- Peer-reviewed literature supporting the intervention
- Industry standards of care]

5. Post-Operative Outcome

[Write 1 paragraph describing:
- Patient's clinical improvement post-surgery
- Pain score changes (e.g., VAS 8/10 to 3/10)
- Return to function
- Validation of medical necessity through positive outcome]

CONCLUSION:

[Write 2-3 bullet points that DIRECTLY refute each denial reason with specific evidence from the records]

Based on the comprehensive documentation provided, I respectfully request that you overturn the denial and approve payment of the denied amount of ${denial_data.get('denied_amount', 0):.2f} for CPT code(s) {denial_data.get('procedure_code')} performed on {denial_data.get('service_date')}.

Each procedure was medically necessary, separately identifiable, and performed to address distinct pathology. The denial reasons stated in the EOB are not supported by the clinical evidence.

ENCLOSED DOCUMENTATION:

[Number each document from the provided context, e.g.:
1. Complete operative report dated [date]
2. MRI report dated [date]
etc.]

I request a written response to this appeal within 30 days as required by state and federal regulations.

**CRITICAL INSTRUCTIONS:**
- Use ONLY facts from the provided documents - do not fabricate details
- Include specific dates, measurements, and clinical findings from the records
- Each of the 5 subsections under CLINICAL JUSTIFICATION is MANDATORY
- For EACH denied service line, you MUST quote the denial code and narrative VERBATIM from the EOB, then respond to it specifically
- Write in professional medical language
- Be detailed and thorough - aim for 800-1200 words total
- Do NOT include provider letterhead or signature block (those are added separately)
- Do NOT reference specific payer guideline names or policy titles (e.g. do NOT say "per UPMC policy" or "per Aetna guidelines"). Instead refer to "the payer's medical policy criteria" or "established clinical guidelines" generically
- Start with "Dear Claims Review Team:" and end after the 30-day request paragraph

**MARKDOWN FORMATTING RULES:**
- Use **bold** for emphasis (e.g., **CPT 27447**)
- Use proper markdown tables with pipes (|) for DENIED SERVICES section
- Use proper bullet points with - or * for lists
- Use blank lines between paragraphs for readability
- Do NOT use HTML tags
- Ensure all tables have header rows with dashes separator (| --- | --- |)
- Keep formatting clean and simple - the UI will handle rendering
"""
        return prompt

    def _prepare_document_context(self, documents: List[Dict]) -> str:
        """
        Prepare document context for LLM.

        CRITICAL: NEVER truncate document text. Pass full text to LLM.
        """
        context_parts = []

        for doc in documents:
            doc_text = f"""
--- Document: {doc.get('document_name', 'Unknown')} ---
Type: {doc.get('document_type', 'Unknown')}
Date: {doc.get('document_date', 'Unknown')}

{doc.get('full_text', '')}

---
"""
            context_parts.append(doc_text)

        full_context = '\n'.join(context_parts)

        # NEVER do this: full_context[:8000]
        # Always return FULL context
        return full_context

    def _prepare_evidence_summary(self, criteria_evaluation: Dict) -> str:
        """Prepare summary of evidence for appeal letter."""
        summary_parts = []

        for criterion in criteria_evaluation.get('criteria', []):
            if criterion.get('met'):
                summary_parts.append(f"- {criterion['description']}: MET")
                for evidence in criterion.get('evidence', [])[:2]:  # Top 2 pieces of evidence
                    summary_parts.append(f"  Evidence: \"{evidence.get('text', '')[:100]}...\"")
            else:
                summary_parts.append(f"- {criterion['description']}: NOT MET")
                if criterion.get('missing_documents'):
                    summary_parts.append(f"  Missing: {criterion['missing_documents']}")

        return '\n'.join(summary_parts)

    def _parse_appeal_letter(self, letter_text: str, denial_data: Dict, criteria_evaluation: Dict) -> Dict:
        """Parse LLM-generated letter into structured format."""

        # Log raw LLM output for debugging
        logger.info(f"[APPEAL PARSE] Raw LLM response length: {len(letter_text)} chars")

        # Simple section extraction with improved header detection
        sections = []
        current_section = None
        current_content = []

        for line in letter_text.split('\n'):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check if this is a section header (improved detection)
            is_header = False
            header_text = line

            # Pattern 1: Lines ending with colon (e.g., "Introduction:")
            if line.endswith(':'):
                is_header = True
                header_text = line.rstrip(':')

            # Pattern 2: ALL UPPERCASE lines
            elif line.isupper() and len(line) > 3:
                is_header = True
                header_text = line

            # Pattern 3: Markdown headers (##, ###, etc.)
            elif line.startswith('#'):
                is_header = True
                header_text = line.lstrip('#').strip()

            # Pattern 4: Bold markdown headers (**Text**)
            elif line.startswith('**') and line.endswith('**'):
                is_header = True
                header_text = line.strip('*').strip()

            # Pattern 5: Numbered sections (1., 2., a., b., etc.)
            elif len(line) > 3 and line[0:2] in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', 'a.', 'b.', 'c.', 'd.', 'e.']:
                # Only treat as header if it's short (likely a title, not a sentence)
                if len(line) < 100:
                    is_header = True
                    header_text = line

            if is_header:
                # Save previous section
                if current_section:
                    content = '\n'.join(current_content).strip()
                    if content:  # Only add sections with content
                        sections.append({
                            "title": current_section,
                            "content": content
                        })
                        logger.info(f"[APPEAL PARSE] Found section: '{current_section}' ({len(content)} chars)")

                # Start new section
                current_section = header_text
                current_content = []
            else:
                # Add to current section content
                current_content.append(line)

        # Save last section
        if current_section:
            content = '\n'.join(current_content).strip()
            if content:  # Only add sections with content
                sections.append({
                    "title": current_section,
                    "content": content
                })
                logger.info(f"[APPEAL PARSE] Found section: '{current_section}' ({len(content)} chars)")

        logger.info(f"[APPEAL PARSE] Total sections extracted: {len(sections)}")

        # Get evidence with bounding boxes
        evidence_references = []
        for criterion in criteria_evaluation.get("criteria", []):
            for evidence in criterion.get("evidence", []):
                evidence_references.append({
                    "criterion_id": criterion["id"],
                    "document_name": evidence.get("document_name"),
                    "text": evidence.get("text"),
                    "page": evidence.get("page"),
                    "bbox": evidence.get("bbox")
                })

        # Get provider info with extraction fallback
        provider_info = self._get_provider_info(denial_data)

        # Build letterhead - address and phone are required by API, others optional
        letterhead = {
            "name": provider_info["name"],
            "address": provider_info.get("address") or "",  # Required by API
            "phone": provider_info.get("phone") or ""       # Required by API
        }
        # Add optional fields only if present
        if provider_info.get("npi"):
            letterhead["npi"] = provider_info["npi"]
        if provider_info.get("tax_id"):
            letterhead["tax_id"] = provider_info["tax_id"]
        if provider_info.get("practice_name"):
            letterhead["practice_name"] = provider_info["practice_name"]

        return {
            "denial_id": denial_data.get('_id'),
            "provider_letterhead": letterhead,
            "sections": sections,
            "evidence_references": evidence_references,
            "enclosed_documents": [d["document_name"] for d in criteria_evaluation.get("top_documents", [])],
            "signature": {
                "name": denial_data.get('provider_name', 'Dr. Provider'),
                "title": "Attending Physician"
            },
            "generated_at": datetime.utcnow()
        }

    def _to_8point(self, bbox: List[Dict]) -> List[float]:
        """
        Convert bounding box to 8-point format for PDFViewer.

        Input: [{"x": 0.1, "y": 0.2}, {"x": 0.9, "y": 0.2}, {"x": 0.9, "y": 0.25}, {"x": 0.1, "y": 0.25}]
        Output: [0.1, 0.2, 0.9, 0.2, 0.9, 0.25, 0.1, 0.25]
        """
        if not bbox or len(bbox) < 4:
            return [0, 0, 1, 0, 1, 1, 0, 1]  # Default full page bbox

        return [
            bbox[0].get("x", 0), bbox[0].get("y", 0),
            bbox[1].get("x", 1), bbox[1].get("y", 0),
            bbox[2].get("x", 1), bbox[2].get("y", 1),
            bbox[3].get("x", 0), bbox[3].get("y", 1)
        ]


# Singleton instance
_processor = None

def get_processor() -> DocumentProcessor:
    """Get or create document processor singleton."""
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor
