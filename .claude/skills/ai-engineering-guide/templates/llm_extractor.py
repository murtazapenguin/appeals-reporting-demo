"""
LLM Extractor Template using penguin-ai-sdk

This template provides structured data extraction from text
using LLMs with Pydantic output validation.
"""

import asyncio
from typing import List, Optional, TypeVar, Type, Generic
from pydantic import BaseModel, Field
from enum import Enum

# penguin-ai-sdk imports
from penguin.llm import create_client, UserMessage, SystemMessage, ChatSession


# Generic type for extraction results
T = TypeVar('T', bound=BaseModel)


class ExtractionConfidence(str, Enum):
    """Confidence levels for extractions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BaseExtraction(BaseModel):
    """Base class for extraction results."""
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    source_text: str = Field(description="Original text that supports this extraction")


class LLMExtractor(Generic[T]):
    """
    Generic LLM-based extractor using penguin-ai-sdk.

    Supports:
    - AWS Bedrock (Claude models)
    - Google Gemini
    - OpenAI GPT models
    - Azure OpenAI

    Usage:
        extractor = LLMExtractor(
            provider="bedrock",
            model="claude-sonnet-4-5",
            system_prompt="You are a medical coder.",
            output_type=List[ICDCode]
        )
        codes = await extractor.extract(document_text)
    """

    def __init__(
        self,
        provider: str = "bedrock",
        model: str = "claude-sonnet-4-5",
        system_prompt: str = "Extract structured information from the text.",
        output_type: Type[T] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ):
        self.client = create_client(provider, model=model)
        self.system_prompt = system_prompt
        self.output_type = output_type
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def extract(
        self,
        text: str,
        additional_context: str = None
    ) -> T:
        """
        Extract structured data from text.

        Args:
            text: Source text to extract from
            additional_context: Optional additional instructions

        Returns:
            Extracted data matching output_type
        """
        messages = [SystemMessage(self.system_prompt)]

        if additional_context:
            messages.append(UserMessage(f"Context: {additional_context}"))

        messages.append(UserMessage(f"Extract from this text:\n\n{text}"))

        result = await self.client.create(
            messages=messages,
            output_format=self.output_type,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return result.content

    async def extract_with_reasoning(
        self,
        text: str
    ) -> dict:
        """
        Extract with visible reasoning chain (Claude Sonnet 4.5).

        Returns dict with 'reasoning' and 'result' keys.
        """
        result = await self.client.create(
            messages=[
                SystemMessage(self.system_prompt),
                UserMessage(f"Analyze step by step:\n\n{text}")
            ],
            output_format=self.output_type,
            thinking=True
        )

        return {
            "reasoning": result.thinking,
            "result": result.content
        }

    async def extract_batch(
        self,
        texts: List[str],
        max_concurrency: int = 5
    ) -> List[T]:
        """
        Extract from multiple texts in parallel.
        """
        semaphore = asyncio.Semaphore(max_concurrency)

        async def extract_one(text: str) -> T:
            async with semaphore:
                return await self.extract(text)

        return await asyncio.gather(*[extract_one(t) for t in texts])


# ============================================
# ICD-10 Code Extraction
# ============================================

class ICDCodeExtraction(BaseModel):
    """ICD-10 code extraction result."""
    code: str = Field(description="ICD-10 code (e.g., J06.9)")
    description: str = Field(description="Code description")
    confidence: float = Field(ge=0, le=100, description="Confidence 0-100")
    supporting_evidence: List[str] = Field(description="Supporting text from document")
    page_references: List[int] = Field(default=[], description="Page numbers where found")


class ICDExtractionResult(BaseModel):
    """Complete ICD extraction result."""
    codes: List[ICDCodeExtraction]
    summary: str = Field(description="Brief summary of findings")
    document_type: str = Field(description="Type of medical document")


ICD_SYSTEM_PROMPT = """You are an expert medical coder specializing in ICD-10 codes.

When analyzing medical documents:
1. Identify all diagnoses, conditions, and procedures
2. Map each to the appropriate ICD-10 code
3. Provide exact supporting text quotes from the document
4. Rate your confidence in each code assignment

Be precise and thorough. Use exact text quotes for supporting_evidence.
Only assign codes when there is clear documentation support."""


async def extract_icd_codes(text: str) -> ICDExtractionResult:
    """
    Extract ICD-10 codes from medical text.

    Args:
        text: Medical document text

    Returns:
        ICDExtractionResult with codes and supporting evidence
    """
    extractor = LLMExtractor(
        provider="bedrock",
        model="claude-sonnet-4-5",
        system_prompt=ICD_SYSTEM_PROMPT,
        output_type=ICDExtractionResult
    )

    return await extractor.extract(text)


# ============================================
# Named Entity Extraction
# ============================================

class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MEDICAL_CONDITION = "medical_condition"
    MEDICATION = "medication"
    PROCEDURE = "procedure"


class ExtractedEntity(BaseModel):
    """A single extracted entity."""
    text: str = Field(description="The entity text")
    entity_type: EntityType
    confidence: float = Field(ge=0, le=1)
    context: str = Field(description="Surrounding context")


class EntityExtractionResult(BaseModel):
    """Entity extraction result."""
    entities: List[ExtractedEntity]


ENTITY_SYSTEM_PROMPT = """Extract named entities from the text.
Identify persons, organizations, locations, dates, medical conditions,
medications, and procedures. Provide the surrounding context for each entity."""


async def extract_entities(text: str) -> EntityExtractionResult:
    """
    Extract named entities from text.

    Args:
        text: Source text

    Returns:
        EntityExtractionResult with all entities
    """
    extractor = LLMExtractor(
        provider="bedrock",
        model="claude-sonnet-4-5",
        system_prompt=ENTITY_SYSTEM_PROMPT,
        output_type=EntityExtractionResult
    )

    return await extractor.extract(text)


# ============================================
# Document Classification
# ============================================

class DocumentCategory(str, Enum):
    MEDICAL_RECORD = "medical_record"
    LAB_REPORT = "lab_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    PRESCRIPTION = "prescription"
    IMAGING_REPORT = "imaging_report"
    OPERATIVE_NOTE = "operative_note"
    PROGRESS_NOTE = "progress_note"
    REFERRAL = "referral"
    INSURANCE = "insurance"
    OTHER = "other"


class ClassificationResult(BaseModel):
    """Document classification result."""
    category: DocumentCategory
    confidence: float = Field(ge=0, le=1)
    indicators: List[str] = Field(description="What indicated this classification")


CLASSIFICATION_PROMPT = """Classify the document type based on its content.
Look for key indicators like headers, formatting, and terminology.
Common medical document types include medical records, lab reports,
discharge summaries, prescriptions, imaging reports, and operative notes."""


async def classify_document(text: str) -> ClassificationResult:
    """
    Classify document type.

    Args:
        text: Document text (first ~5000 chars recommended)

    Returns:
        ClassificationResult with category and confidence
    """
    extractor = LLMExtractor(
        provider="bedrock",
        model="claude-sonnet-4-5",
        system_prompt=CLASSIFICATION_PROMPT,
        output_type=ClassificationResult
    )

    # Use first 5000 chars for classification
    return await extractor.extract(text[:5000])


# ============================================
# Custom Extraction with Tools
# ============================================

from penguin.tools import tool, ToolExecutor


@tool
def validate_icd_code(code: str) -> dict:
    """Validate an ICD-10 code format and return details.

    Args:
        code: ICD-10 code to validate
    """
    # Mock validation - in production, use real ICD database
    import re
    pattern = r'^[A-Z]\d{2}(\.\d{1,2})?$'

    is_valid = bool(re.match(pattern, code))
    return {
        "code": code,
        "is_valid": is_valid,
        "format": "ICD-10-CM" if is_valid else "invalid"
    }


@tool
def search_icd_database(query: str, limit: int = 5) -> List[dict]:
    """Search ICD-10 database for matching codes.

    Args:
        query: Search query
        limit: Maximum results
    """
    # Mock search - in production, use real database
    return [
        {"code": "J06.9", "description": "Acute upper respiratory infection", "score": 0.95},
        {"code": "J18.9", "description": "Pneumonia, unspecified organism", "score": 0.80}
    ][:limit]


async def extract_with_tools(text: str) -> dict:
    """
    Extract ICD codes with tool-assisted validation.

    Uses tool calling to validate and search for codes.
    """
    client = create_client("bedrock", model="claude-sonnet-4-5")
    executor = ToolExecutor([validate_icd_code, search_icd_database])

    # Initial extraction request
    result = await client.create(
        messages=[
            SystemMessage("Extract ICD codes. Use tools to validate and search for codes."),
            UserMessage(text)
        ],
        tools=executor.to_provider_format("bedrock")
    )

    # Handle tool calls
    if result.has_tool_calls:
        tool_results = await executor.execute_parallel(result.tool_calls)

        # Continue with tool results
        messages = [
            UserMessage(text),
            result.to_message()
        ]

        for tc, tr in zip(result.tool_calls, tool_results):
            messages.append(tr.to_message(tc.call_id))

        final = await client.create(messages=messages)
        return {"content": final.content, "tool_calls": len(result.tool_calls)}

    return {"content": result.content, "tool_calls": 0}


# CLI usage
if __name__ == "__main__":
    import sys

    async def main():
        sample_text = """
        Patient: John Doe
        Date: 2024-01-15

        Chief Complaint: Fever and cough for 3 days

        Assessment:
        1. Acute upper respiratory infection
        2. Rule out pneumonia

        Plan:
        - Chest X-ray
        - Amoxicillin 500mg TID x 7 days
        - Follow up in 1 week
        """

        print("=== ICD Code Extraction ===")
        icd_result = await extract_icd_codes(sample_text)
        print(f"Found {len(icd_result.codes)} codes:")
        for code in icd_result.codes:
            print(f"  {code.code}: {code.description} ({code.confidence}%)")

        print("\n=== Document Classification ===")
        class_result = await classify_document(sample_text)
        print(f"Category: {class_result.category}")
        print(f"Confidence: {class_result.confidence}")

        print("\n=== Entity Extraction ===")
        entity_result = await extract_entities(sample_text)
        for entity in entity_result.entities:
            print(f"  {entity.entity_type}: {entity.text}")

    asyncio.run(main())
