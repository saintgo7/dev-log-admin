#!/bin/bash
#
# Dev Log Admin - Status Check
# 어드민 서버 상태를 확인합니다
#

ADMIN_DIR="$HOME/dev-log-admin"
PID_FILE="$ADMIN_DIR/.server.pid"
PORT=8100

echo ""
echo "=========================================="
echo "📊 Dev Log Admin - Status"
echo "=========================================="
echo ""

# Check PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")

    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Server is running"
        echo "   PID: $PID"
        echo "   URL: http://localhost:$PORT"
        echo ""

        # Check if port is listening
        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "✅ Port $PORT is listening"
        else
            echo "⚠️  Port $PORT is not listening"
        fi

        # Show memory usage
        MEM=$(ps -o rss= -p $PID | awk '{printf "%.1f MB", $1/1024}')
        echo "   Memory: $MEM"

        # Check uptime
        START_TIME=$(ps -o lstart= -p $PID)
        echo "   Started: $START_TIME"

        # Show recent log entries
        if [ -f "$ADMIN_DIR/server.log" ]; then
            echo ""
            echo "📝 Recent logs (last 5 lines):"
            echo "----------------------------------------"
            tail -5 "$ADMIN_DIR/server.log"
        fi
    else
        echo "❌ Server is not running"
        echo "   (PID file exists but process $PID not found)"
        rm -f "$PID_FILE"
    fi
else
    echo "❌ Server is not running"
    echo "   (No PID file found)"

    # Check if any server is running on the port
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        PROC_PID=$(lsof -ti:$PORT)
        echo ""
        echo "⚠️  Warning: Port $PORT is in use by another process (PID: $PROC_PID)"
        echo "   To stop it: kill $PROC_PID"
    fi
fi

echo ""
echo "📊 Statistics:"

# Count projects
if [ -f "$ADMIN_DIR/config.json" ]; then
    PROJECTS=$(python3 -c "import json; print(len(json.load(open('$ADMIN_DIR/config.json'))['projects']))" 2>/dev/null || echo "0")
    echo "   Projects: $PROJECTS"
fi

# Count commits
if [ -f "$ADMIN_DIR/devlog.db" ]; then
    COMMITS=$(sqlite3 "$ADMIN_DIR/devlog.db" "SELECT COUNT(*) FROM commits" 2>/dev/null || echo "0")
    echo "   Commits: $COMMITS"
fi

echo ""
