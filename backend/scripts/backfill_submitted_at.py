"""
Backfill submitted_at field for existing submitted appeals.

This script populates the submitted_at timestamp for all denials with status:
- submitted
- approved
- denied

For each denial, it attempts to use the package_generated_at from the appeal_packages
collection as the submission date proxy. If no appeal package exists, it falls back
to the denial's updated_at timestamp.

This script is idempotent and safe to run multiple times.
"""

import asyncio
from datetime import datetime
import os
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import denials_collection, appeal_packages_collection

async def backfill_submitted_at():
    """Backfill submitted_at for existing submitted/approved/denied appeals."""

    print("[BACKFILL] Starting submitted_at backfill...")

    # Find all denials that are submitted/approved/denied but missing submitted_at
    query = {
        "status": {"$in": ["submitted", "approved", "denied"]},
        "submitted_at": None
    }

    denials = await denials_collection.find(query).to_list(10000)

    if not denials:
        print("[BACKFILL] No denials found needing backfill. All up to date!")
        return

    print(f"[BACKFILL] Found {len(denials)} denials to backfill")

    updated_count = 0
    failed_count = 0

    for denial in denials:
        denial_id = str(denial["_id"])
        claim_number = denial.get("claim_number", "unknown")

        try:
            # Look up appeal package for this denial
            appeal_package = await appeal_packages_collection.find_one({"denial_id": denial_id})

            # Determine submission date
            if appeal_package and appeal_package.get("package_generated_at"):
                # Use package generation date as submission date proxy
                submitted_at = appeal_package["package_generated_at"]
                source = "appeal_package.package_generated_at"
            else:
                # Fallback to denial's updated_at
                submitted_at = denial.get("updated_at", datetime.utcnow())
                source = "denial.updated_at (fallback)"

            # Update denial with submitted_at
            result = await denials_collection.update_one(
                {"_id": denial["_id"]},
                {"$set": {"submitted_at": submitted_at}}
            )

            if result.modified_count > 0:
                updated_count += 1
                print(f"[BACKFILL] ✓ Updated {claim_number} (ID: {denial_id[:8]}...) - Source: {source}")
            else:
                print(f"[BACKFILL] ⚠ No update for {claim_number} (ID: {denial_id[:8]}...) - already has submitted_at?")

        except Exception as e:
            failed_count += 1
            print(f"[BACKFILL] ✗ Failed to update {claim_number} (ID: {denial_id[:8]}...): {str(e)}")

    print("\n" + "="*60)
    print(f"[BACKFILL] Complete!")
    print(f"  Updated: {updated_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total processed: {len(denials)}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(backfill_submitted_at())
