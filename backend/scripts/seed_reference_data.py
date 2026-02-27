"""Seed reference data (payers and providers) into MongoDB."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.db_utils import reference_data_collection


PAYERS = [
    "Aetna",
    "Blue Cross Blue Shield",
    "Gotham Health Insurance",
    "United Healthcare"
]

PROVIDERS = [
    {"name": "Dr. Emily Parker", "practice": "Parker Spine Institute"},
    {"name": "Dr. Harvey Dent", "practice": "Dent Reconstructive Surgery"},
    {"name": "Dr. Leslie Thompkins", "practice": "Thompkins Family Medicine"},
    {"name": "Dr. Michael Torres", "practice": "Torres Emergency Medicine"},
    {"name": "Dr. Sarah Wilson", "practice": "Wilson Orthopedic Center"},
    {"name": "Dr. Thomas Elliot", "practice": "Elliot Neurosurgery Group"},
]


async def seed():
    # Upsert payers
    await reference_data_collection.update_one(
        {"type": "payers"},
        {"$set": {"type": "payers", "values": PAYERS}},
        upsert=True
    )
    print(f"Seeded {len(PAYERS)} payers")

    # Upsert providers
    await reference_data_collection.update_one(
        {"type": "providers"},
        {"$set": {"type": "providers", "values": PROVIDERS}},
        upsert=True
    )
    print(f"Seeded {len(PROVIDERS)} providers")


if __name__ == "__main__":
    asyncio.run(seed())
