import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB / DocumentDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "claim_appeals")
MONGODB_TLS = os.getenv("MONGODB_TLS", "false").lower() == "true"
MONGODB_TLS_CA_FILE = os.getenv("MONGODB_TLS_CA_FILE", "/app/global-bundle.pem")

# JWT
JWT_SECRET = os.getenv("JWT_SECRET", "claim-appeals-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Azure OCR
AZURE_OCR_ENDPOINT = os.getenv("AZURE_OCR_ENDPOINT", "")
AZURE_OCR_SECRET_KEY = os.getenv("AZURE_OCR_SECRET_KEY", "")

# AWS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
