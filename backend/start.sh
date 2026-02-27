#!/bin/bash

# Start script for Healthcare Claim Denial Appeal Management API

# Activate virtual environment
source venv/bin/activate

# Start the server
echo "Starting FastAPI backend server on http://localhost:8000..."
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
