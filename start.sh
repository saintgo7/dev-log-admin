#!/bin/bash
#
# Dev Log Admin - Quick Start Script
# 통합 어드민 대시보드를 시작하고 브라우저를 엽니다
#

set -e

ADMIN_DIR="$HOME/dev-log-admin"
PORT=8100
PID_FILE="$ADMIN_DIR/.server.pid"

echo ""
echo "=========================================="
echo "📊 Dev Log Admin - Starting..."
echo "=========================================="
echo ""

# Check if server is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Server is already running (PID: $PID)"
        echo "📊 Dashboard: http://localhost:$PORT"
        echo ""

        # Just open browser
        open "http://localhost:$PORT"
        exit 0
    else
        # PID file exists but process is dead
        rm -f "$PID_FILE"
    fi
fi

# Check if port is in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use by another process"
    echo ""
    echo "To stop it:"
    echo "  lsof -ti:$PORT | xargs kill"
    echo ""
    exit 1
fi

# Change to admin directory
cd "$ADMIN_DIR"

# Check Python dependencies
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "⚠️  Missing Python packages"
    echo ""
    echo "Installing FastAPI and Uvicorn..."
    pip3 install fastapi uvicorn
    echo ""
fi

# Start server in background
echo "🚀 Starting server..."
nohup python3 server.py > "$ADMIN_DIR/server.log" 2>&1 &
SERVER_PID=$!

# Save PID
echo $SERVER_PID > "$PID_FILE"

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Check if server is running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "✅ Server started successfully (PID: $SERVER_PID)"
    echo ""
    echo "=========================================="
    echo "📊 Dev Log Admin Dashboard"
    echo "=========================================="
    echo ""
    echo "🌐 URL: http://localhost:$PORT"
    echo "📖 API Docs: http://localhost:$PORT/docs"
    echo "📝 Logs: $ADMIN_DIR/server.log"
    echo ""
    echo "To stop the server:"
    echo "  $ADMIN_DIR/stop.sh"
    echo "  or: kill $SERVER_PID"
    echo ""

    # Open browser
    sleep 1
    open "http://localhost:$PORT"
else
    echo "❌ Failed to start server"
    echo ""
    echo "Check logs:"
    echo "  tail -f $ADMIN_DIR/server.log"
    rm -f "$PID_FILE"
    exit 1
fi
