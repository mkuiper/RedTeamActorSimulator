#!/bin/bash

# Start Frontend Only

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT/frontend"

echo "Starting Red Team Actor Simulator - Frontend UI"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Dependencies not found. Run ./start.sh first to set up."
    exit 1
fi

echo "Frontend UI starting on http://localhost:5173"
echo ""
echo "Note: Make sure backend is running on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

npm run dev
