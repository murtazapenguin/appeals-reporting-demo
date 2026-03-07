# One-time seed (e.g. for production)

Use this to seed the database **once** for a deployed environment (e.g. the DB your Vercel frontend talks to). The seed creates demo users, denials (including rejected appeals), practices, payers, documents, and comparison data.

## Option 1: Run from your machine (recommended)

1. **Get your production MongoDB connection string**  
   From your backend host (e.g. MongoDB Atlas, DocumentDB): copy the URI and database name.

2. **From the repo root**, run the seed **once** with that URL:

   ```bash
   cd backend
   MONGODB_URL='mongodb+srv://USER:PASSWORD@cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority' \
   DATABASE_NAME='claim_appeals' \
   python seed_comprehensive.py
   ```

   Or use the script (loads `backend/.env` if present; override with env vars):

   ```bash
   MONGODB_URL='mongodb+srv://...' DATABASE_NAME='claim_appeals' ./backend/scripts/seed_once.sh
   ```

3. **Security:** Do not commit the URL or run this in a logged script. Use env vars or a one-off `.env` you don’t commit.

4. **After running:** Your deployed app (e.g. Vercel frontend + your API) will show the seeded data. You only need to run this once per environment unless you reset the DB.

## Option 2: Run on the backend server

If your backend runs on a server (e.g. EKS, EC2, Railway):

1. SSH or open a shell where the backend runs and where `MONGODB_URL` already points to the right DB.
2. From the app directory:

   ```bash
   cd backend
   python seed_comprehensive.py
   ```

   Or with Docker:  
   `docker-compose exec backend python seed_comprehensive.py`

## Credentials after seeding

- **Email:** `demo@penguinai.com`
- **Password:** `demo123`
