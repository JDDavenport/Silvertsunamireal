#!/bin/bash
# Start ACQUISITOR DISPATCH System

cd "$(dirname "$0")"

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt

# Create data directory
mkdir -p data

# Run based on argument
if [ "$1" == "server" ]; then
    echo "🌐 Starting DISPATCH API Server..."
    echo "   URL: http://localhost:3001"
    echo ""
    python src/orchestrator.py server
elif [ "$1" == "daemon" ]; then
    echo "🤖 Starting DISPATCH Orchestrator Daemon..."
    echo "   Database: data/dispatch.db"
    echo "   Press Ctrl+C to stop"
    echo ""
    python src/orchestrator.py
else
    echo "ACQUISITOR DISPATCH System"
    echo ""
    echo "Usage:"
    echo "  ./start.sh server   - Start API server"
    echo "  ./start.sh daemon   - Start orchestrator daemon"
    echo ""
fi
