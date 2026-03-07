# Claim Appeals V2

Healthcare Claim Denial Appeal Management System - A full-stack application for managing and appealing healthcare claim denials using AI-powered document analysis.

## Features

- **Denial Queue Management** - View, filter, and prioritize claim denials
- **CSV Import** - Bulk upload denials from CSV files
- **Document Management** - Upload and organize patient medical records (PDFs)
- **AI-Powered Evidence Extraction** - Automatically extract relevant evidence from medical documents using OCR and LLM
- **Bounding Box Highlighting** - Click on evidence to highlight source text in the PDF viewer
- **Criteria Evaluation** - Match documents against payer-specific medical policies
- **Appeal Letter Generation** - Auto-generate appeal letters with markdown editing support
- **JWT Authentication** - Secure user authentication

## Tech Stack

### Frontend
- React 18 with Vite
- Tailwind CSS v4
- React Router v6
- PDF Viewer with bounding box support
- React Markdown for appeal letter editing

### Backend
- FastAPI (Python 3.11)
- MongoDB with Motor async driver
- Pydantic v2 for data validation
- JWT authentication with python-jose

### AI/ML
- **OCR**: Azure Document Intelligence
- **LLM**: Google Gemini (gemini-3-flash-preview)
- **SDK**: penguin-ai-sdk for unified AI operations

### Infrastructure
- Docker & Docker Compose
- Nginx for frontend serving
- MongoDB 7.0
- AWS S3 for document storage (bucket: `appeals-pgn-dev`)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)
- MongoDB (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Penguin-AI-Corp/pgn-appeals-claim.git
   cd pgn-appeals-claim
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start all services**
   ```bash
   make dev
   # Or: docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:80
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install /tmp/penguin_ai_sdk-0.1.3-py3-none-any.whl[cpu]

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the server
uvicorn app:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Demo mode (no backend/DB)

To run the frontend with **fixed mock data** and no backend (e.g. for Vercel or a quick demo):

1. In `frontend`, set `VITE_DEMO_MODE=true` (e.g. in `.env` or in Vercel → Project → Settings → Environment Variables).
2. Build and run: `npm run build && npm run preview` (or deploy to Vercel).
3. Log in with any credentials; denials list, denial detail, documents, criteria, and appeal letter use mock data. Writes (create, update, upload, submit) are no-ops and are not persisted.

## Environment Variables

Create a `.env` file in the root directory:

```env
# JWT Configuration
JWT_SECRET=your-secret-key-change-in-production

# Azure Document Intelligence (OCR)
AZURE_OCR_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_OCR_SECRET_KEY=your-azure-key

# AWS Credentials (for Bedrock)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_SESSION_TOKEN=your-session-token
AWS_REGION=us-east-1

# Google Gemini
GEMINI_API_KEY=your-gemini-key

# S3 Document Storage
S3_BUCKET=appeals-pgn-dev
S3_PREFIX=documents
S3_PRESIGNED_EXPIRATION=3600

# Application
LOG_LEVEL=INFO
VITE_API_BASE_URL=http://localhost:8000/api
```

## Project Structure

```
claim-appeals-v2/
├── backend/
│   ├── app.py                 # FastAPI application entry
│   ├── routes/                # API route handlers
│   │   ├── auth_routes.py
│   │   ├── denial_routes.py
│   │   ├── document_routes.py
│   │   ├── criteria_evaluation_routes.py
│   │   └── appeal_routes.py
│   ├── models/                # Pydantic models
│   ├── services/
│   │   └── ai_processor.py    # AI pipeline (OCR, LLM, evidence extraction)
│   ├── utils/
│   │   └── db_utils.py        # MongoDB utilities
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── DenialDetail.jsx
│   │   │   ├── DenialQueue.jsx
│   │   │   ├── PDFViewer.jsx
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.js         # API client
│   │   └── App.jsx
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml         # Development configuration
├── docker-compose.prod.yml    # Production configuration
├── Makefile                   # Convenience commands
└── .env.example
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Denials
- `GET /api/denials` - List all denials
- `GET /api/denials/{id}` - Get denial details
- `POST /api/denials/upload-csv` - Upload denials from CSV

### Documents
- `GET /api/documents/patient/{patient_id}` - Get patient documents
- `POST /api/documents/upload/{denial_id}` - Upload document for denial
- `GET /api/documents/{id}/pdf` - Get PDF file

### Criteria Evaluation
- `POST /api/criteria/evaluate/{denial_id}` - Run AI evidence extraction
- `GET /api/criteria/results/{denial_id}` - Get evaluation results

### Appeals
- `POST /api/appeals/generate/{denial_id}` - Generate appeal letter
- `GET /api/appeals/letter/{denial_id}` - Get appeal letter

## Makefile Commands

```bash
make dev          # Start development environment
make dev-build    # Rebuild and start development
make dev-down     # Stop development environment

make prod         # Start production environment
make prod-build   # Rebuild and start production
make prod-down    # Stop production environment

make logs         # View all logs
make logs-backend # View backend logs
make health       # Check service health
make gitleaks     # Run security scan
make seed         # Seed sample data (Docker)
```

**One-time seed for production / deployed DB**  
To populate the database your deployed app uses (e.g. after deploying to Vercel), run the seed once from your machine with that database URL. See [backend/scripts/SEED_ONE_TIME.md](backend/scripts/SEED_ONE_TIME.md) for steps. Example:

```bash
cd backend
MONGODB_URL='mongodb+srv://...' DATABASE_NAME='claim_appeals' python seed_comprehensive.py
```

## AI Processing Pipeline

1. **Document Filtering** - Filter documents by date range (90 days before service to denial date)
2. **OCR Processing** - Extract text and bounding boxes using Azure Document Intelligence
3. **Relevancy Scoring** - Score documents against denial criteria using Gemini
4. **Document Shortlisting** - Select top 3 most relevant documents
5. **Evidence Extraction** - Extract specific evidence with page numbers and bounding boxes
6. **Appeal Generation** - Generate structured appeal letter using extracted evidence

## Default Credentials

For development/demo:
- **Email**: demo@example.com
- **Password**: demo123

## Security

- Gitleaks configured for secret scanning
- JWT-based authentication
- CORS configured for frontend origin
- Security headers in Nginx configuration
- Environment variables for all secrets

## License

Proprietary - Penguin AI Corp

## Support

For issues and feature requests, please contact the development team.
