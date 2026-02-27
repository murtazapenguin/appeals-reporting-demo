"""
S3 Storage Utility for Document Management

Handles upload, download, and presigned URL generation for documents stored in S3.
Bucket: appeals-pgn-dev
"""

import boto3
import os
import logging
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
import io

logger = logging.getLogger("s3_storage")

# S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET", "appeals-pgn-dev")
S3_REGION = os.getenv("S3_REGION", "us-east-2")
S3_PREFIX = os.getenv("S3_PREFIX", "documents")  # Base prefix for all documents

# Presigned URL expiration (in seconds)
PRESIGNED_URL_EXPIRATION = int(os.getenv("S3_PRESIGNED_EXPIRATION", 3600))  # 1 hour default


def get_s3_client():
    """Get S3 client using default credential chain (IAM role, env vars, etc.)."""
    return boto3.client("s3", region_name=S3_REGION)


def get_s3_key(patient_id: str, document_id: str, filename: str) -> str:
    """
    Generate S3 key for a document.

    Format: documents/{patient_id}/{document_id}/{filename}
    """
    return f"{S3_PREFIX}/{patient_id}/{document_id}/{filename}"


async def upload_to_s3(
    file_content: bytes,
    patient_id: str,
    document_id: str,
    filename: str,
    content_type: str = "application/pdf"
) -> dict:
    """
    Upload a document to S3.

    Args:
        file_content: File bytes to upload
        patient_id: Patient ID for folder structure
        document_id: Document ID for folder structure
        filename: Original filename
        content_type: MIME type of the file

    Returns:
        dict with s3_key and s3_uri
    """
    s3_client = get_s3_client()
    s3_key = get_s3_key(patient_id, document_id, filename)

    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=file_content,
            ContentType=content_type,
            Metadata={
                "patient_id": patient_id,
                "document_id": document_id,
                "original_filename": filename
            }
        )

        s3_uri = f"s3://{S3_BUCKET}/{s3_key}"
        logger.info(f"[S3 UPLOAD] Uploaded {filename} to {s3_uri}")

        return {
            "s3_key": s3_key,
            "s3_uri": s3_uri,
            "bucket": S3_BUCKET
        }

    except ClientError as e:
        logger.error(f"[S3 UPLOAD ERROR] Failed to upload {filename}: {str(e)}")
        raise Exception(f"Failed to upload to S3: {str(e)}")


async def download_from_s3(s3_key: str) -> bytes:
    """
    Download a document from S3.

    Args:
        s3_key: The S3 object key

    Returns:
        File content as bytes
    """
    s3_client = get_s3_client()

    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        content = response["Body"].read()
        logger.info(f"[S3 DOWNLOAD] Downloaded {s3_key} ({len(content)} bytes)")
        return content

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "NoSuchKey":
            logger.error(f"[S3 DOWNLOAD ERROR] Object not found: {s3_key}")
            raise FileNotFoundError(f"S3 object not found: {s3_key}")
        logger.error(f"[S3 DOWNLOAD ERROR] Failed to download {s3_key}: {str(e)}")
        raise Exception(f"Failed to download from S3: {str(e)}")


async def download_to_temp_file(s3_key: str, temp_dir: str = "/tmp") -> str:
    """
    Download a document from S3 to a temporary file.

    Args:
        s3_key: The S3 object key
        temp_dir: Directory for temporary file

    Returns:
        Path to the temporary file
    """
    content = await download_from_s3(s3_key)

    # Extract filename from key
    filename = s3_key.split("/")[-1]
    temp_path = os.path.join(temp_dir, filename)

    with open(temp_path, "wb") as f:
        f.write(content)

    logger.info(f"[S3 DOWNLOAD] Saved to temp file: {temp_path}")
    return temp_path


def generate_presigned_url(s3_key: str, expiration: int = None) -> str:
    """
    Generate a presigned URL for accessing a document.

    Args:
        s3_key: The S3 object key
        expiration: URL expiration in seconds (default: PRESIGNED_URL_EXPIRATION)

    Returns:
        Presigned URL string
    """
    s3_client = get_s3_client()
    expiration = expiration or PRESIGNED_URL_EXPIRATION

    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": s3_key
            },
            ExpiresIn=expiration
        )
        return url

    except ClientError as e:
        logger.error(f"[S3 PRESIGN ERROR] Failed to generate URL for {s3_key}: {str(e)}")
        raise Exception(f"Failed to generate presigned URL: {str(e)}")


async def delete_from_s3(s3_key: str) -> bool:
    """
    Delete a document from S3.

    Args:
        s3_key: The S3 object key

    Returns:
        True if deleted successfully
    """
    s3_client = get_s3_client()

    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        logger.info(f"[S3 DELETE] Deleted {s3_key}")
        return True

    except ClientError as e:
        logger.error(f"[S3 DELETE ERROR] Failed to delete {s3_key}: {str(e)}")
        raise Exception(f"Failed to delete from S3: {str(e)}")


async def check_s3_object_exists(s3_key: str) -> bool:
    """
    Check if an object exists in S3.

    Args:
        s3_key: The S3 object key

    Returns:
        True if object exists
    """
    s3_client = get_s3_client()

    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=s3_key)
        return True
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "404":
            return False
        raise


# ============================================================
# Page Image Caching Functions
# ============================================================

def get_page_image_s3_key(patient_id: str, document_id: str, page_number: int) -> str:
    """
    Generate S3 key for a cached page image.

    Format: documents/{patient_id}/{document_id}/pages/page_{n}.png
    """
    return f"{S3_PREFIX}/{patient_id}/{document_id}/pages/page_{page_number}.png"


async def check_page_image_exists(patient_id: str, document_id: str, page_number: int) -> bool:
    """Check if a cached page image exists in S3."""
    s3_key = get_page_image_s3_key(patient_id, document_id, page_number)
    return await check_s3_object_exists(s3_key)


async def upload_page_image(
    image_bytes: bytes,
    patient_id: str,
    document_id: str,
    page_number: int
) -> str:
    """
    Upload a page image to S3 cache.

    Returns:
        S3 key of the uploaded image
    """
    s3_client = get_s3_client()
    s3_key = get_page_image_s3_key(patient_id, document_id, page_number)

    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=image_bytes,
            ContentType="image/png",
            CacheControl="public, max-age=31536000"  # Cache for 1 year
        )
        logger.info(f"[S3 CACHE] Uploaded page image: {s3_key}")
        return s3_key

    except ClientError as e:
        logger.error(f"[S3 CACHE ERROR] Failed to upload page image: {str(e)}")
        raise Exception(f"Failed to upload page image: {str(e)}")


def get_page_image_presigned_url(patient_id: str, document_id: str, page_number: int, expiration: int = None) -> str:
    """
    Get presigned URL for a cached page image.

    Args:
        patient_id: Patient ID
        document_id: Document ID
        page_number: Page number (1-indexed)
        expiration: URL expiration in seconds

    Returns:
        Presigned URL for the page image
    """
    s3_key = get_page_image_s3_key(patient_id, document_id, page_number)
    return generate_presigned_url(s3_key, expiration)


async def list_patient_documents(patient_id: str) -> list:
    """
    List all documents for a patient in S3.

    Args:
        patient_id: Patient ID

    Returns:
        List of S3 keys
    """
    s3_client = get_s3_client()
    prefix = f"{S3_PREFIX}/{patient_id}/"

    try:
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=prefix
        )

        keys = []
        for obj in response.get("Contents", []):
            keys.append(obj["Key"])

        return keys

    except ClientError as e:
        logger.error(f"[S3 LIST ERROR] Failed to list documents for {patient_id}: {str(e)}")
        raise Exception(f"Failed to list S3 objects: {str(e)}")
