#!/bin/bash

# Start Backend Only

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT/backend"

echo "Starting Red Team Actor Simulator - Backend API"
echo ""

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "Error: .env file not found in project root!"
    echo "Copy .env.example to .env and add your API keys."
    exit 1
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run ./start.sh first to set up."
    exit 1
fi

source venv/bin/activate

echo "Backend API starting on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
