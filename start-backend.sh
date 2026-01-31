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

set -a
# shellcheck disable=SC1091
source ../.env
set +a

is_true() {
    case "${1,,}" in
        true|1|yes|y) return 0 ;;
        *) return 1 ;;
    esac
}

HOST_VALUE="${HOST:-0.0.0.0}"
PORT_VALUE="${PORT:-8000}"
RELOAD_FLAG="--reload"
if ! is_true "${DEBUG:-}"; then
    RELOAD_FLAG=""
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run ./start.sh first to set up."
    exit 1
fi

source venv/bin/activate

echo "Backend API starting on http://localhost:${PORT_VALUE}"
echo "API Documentation: http://localhost:${PORT_VALUE}/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -m uvicorn app.main:app --host "$HOST_VALUE" --port "$PORT_VALUE" $RELOAD_FLAG
