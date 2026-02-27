from fastapi import APIRouter
from utils.db_utils import reference_data_collection

router = APIRouter(prefix="/api/reference-data", tags=["Reference Data"])


@router.get("/payers")
async def get_payers():
    """Get all payers."""
    doc = await reference_data_collection.find_one({"type": "payers"})
    if not doc:
        return []
    return doc.get("values", [])


@router.get("/providers")
async def get_providers():
    """Get all providers."""
    doc = await reference_data_collection.find_one({"type": "providers"})
    if not doc:
        return []
    return doc.get("values", [])
