#!/usr/bin/env bash
# One-time seed for the database (e.g. production or staging).
# Usage:
#   From repo root:  backend/scripts/seed_once.sh
#   From backend:    scripts/seed_once.sh
# Set MONGODB_URL (and optionally DATABASE_NAME) before running, or use a .env file in backend/.

set -e
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BACKEND_DIR"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

if [ -z "$MONGODB_URL" ]; then
  echo "Error: MONGODB_URL is not set. Set it to your database connection string (e.g. MongoDB Atlas URI)."
  echo "Example: MONGODB_URL='mongodb+srv://user:pass@cluster.mongodb.net/' DATABASE_NAME='claim_appeals' $0"
  exit 1
fi

# Optional: warn if targeting what looks like localhost (avoid accidental prod seed with wrong env)
if [[ "$MONGODB_URL" == *"localhost"* ]] || [[ "$MONGODB_URL" == *"127.0.0.1"* ]]; then
  echo "Note: MONGODB_URL contains localhost. Seeding local database."
fi

echo "Seeding database (MONGODB_URL host is set; DATABASE_NAME=${DATABASE_NAME:-claim_appeals})."
python seed_comprehensive.py
echo "Done."
