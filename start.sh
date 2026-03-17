#!/bin/bash
# OpenClaw Monitor Start Script

cd "$(dirname "$0")"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install flask flask-cors
fi

# Start the server
echo "🚀 Starting OpenClaw Monitor..."
echo "📍 Dashboard: http://localhost:5050"
echo "Press Ctrl+C to stop"
echo ""

python3 server.py