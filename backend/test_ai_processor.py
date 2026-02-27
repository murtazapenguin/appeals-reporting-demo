"""
Test script for AI processor integration.

Tests:
1. Penguin SDK imports
2. OCR provider initialization
3. LLM client initialization
"""

import asyncio
import sys
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_imports():
    """Test penguin-ai-sdk imports."""
    logger.info("[TEST] Testing penguin-ai-sdk imports...")

    try:
        from penguin.ocr import AzureOCRProvider
        from penguin.llm import create_client, UserMessage, SystemMessage
        logger.info("[TEST] ✓ Penguin SDK imports successful")
        return True
    except ImportError as e:
        logger.error(f"[TEST] ✗ Import failed: {str(e)}")
        return False


async def test_ocr_provider():
    """Test OCR provider initialization."""
    logger.info("[TEST] Testing OCR provider initialization...")

    try:
        from penguin.ocr import AzureOCRProvider
        ocr = AzureOCRProvider()
        logger.info("[TEST] ✓ Azure OCR provider initialized")
        return True
    except Exception as e:
        logger.error(f"[TEST] ✗ OCR initialization failed: {str(e)}")
        return False


async def test_llm_client():
    """Test LLM client initialization."""
    logger.info("[TEST] Testing LLM client initialization...")

    try:
        from penguin.llm import create_client
        llm = create_client("bedrock", model="anthropic.claude-3-5-sonnet-20241022-v2:0")
        logger.info("[TEST] ✓ Bedrock Claude LLM initialized")
        return True
    except Exception as e:
        logger.error(f"[TEST] ✗ LLM initialization failed: {str(e)}")
        return False


async def test_processor():
    """Test DocumentProcessor initialization."""
    logger.info("[TEST] Testing DocumentProcessor initialization...")

    try:
        from services.ai_processor import get_processor
        processor = get_processor()
        logger.info("[TEST] ✓ DocumentProcessor initialized")
        return True
    except Exception as e:
        logger.error(f"[TEST] ✗ DocumentProcessor initialization failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    logger.info("="*60)
    logger.info("AI Processor Integration Tests")
    logger.info("="*60)

    results = []

    # Test 1: Imports
    results.append(await test_imports())

    # Test 2: OCR Provider
    results.append(await test_ocr_provider())

    # Test 3: LLM Client
    results.append(await test_llm_client())

    # Test 4: Processor
    results.append(await test_processor())

    # Summary
    logger.info("="*60)
    logger.info(f"Tests Passed: {sum(results)}/{len(results)}")
    logger.info("="*60)

    if all(results):
        logger.info("✓ All tests passed! AI processor is ready.")
        return 0
    else:
        logger.error("✗ Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
