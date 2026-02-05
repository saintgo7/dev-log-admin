#!/bin/bash
#
# Dev Log Admin - Stop Script
# 실행 중인 어드민 서버를 중지합니다
#

ADMIN_DIR="$HOME/dev-log-admin"
PID_FILE="$ADMIN_DIR/.server.pid"

echo ""
echo "=========================================="
echo "🛑 Dev Log Admin - Stopping..."
echo "=========================================="
echo ""

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  No PID file found"
    echo ""
    echo "Checking for running processes..."
    PIDS=$(pgrep -f "python3.*server.py")

    if [ -n "$PIDS" ]; then
        echo "Found running server processes: $PIDS"
        echo "$PIDS" | xargs kill
        echo "✅ Stopped all dev-log admin servers"
    else
        echo "ℹ️  No running server found"
    fi
    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "🛑 Stopping server (PID: $PID)..."
    kill $PID

    # Wait for process to terminate
    for i in {1..10}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            break
        fi
        sleep 0.5
    done

    # Force kill if still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Force killing server..."
        kill -9 $PID
    fi

    rm -f "$PID_FILE"
    echo "✅ Server stopped successfully"
else
    echo "ℹ️  Server is not running (PID $PID not found)"
    rm -f "$PID_FILE"
fi

echo ""
