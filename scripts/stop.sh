#!/bin/bash
#
# Dev Log Admin - Unified Stop Script
# Usage: ./scripts/stop.sh [all|legacy|backend|frontend]
#

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PIDS_DIR="$PROJECT_DIR/.pids"

TARGET="${1:-all}"

stop_service() {
    local name="$1"
    local pid_file="$PIDS_DIR/$name.pid"

    if [ ! -f "$pid_file" ]; then
        echo "[$name] Not running (no PID file)"
        return 0
    fi

    PID=$(cat "$pid_file")

    if ps -p "$PID" > /dev/null 2>&1; then
        echo "[$name] Stopping (PID: $PID)..."
        kill "$PID"

        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                break
            fi
            sleep 0.5
        done

        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "[$name] Force killing..."
            kill -9 "$PID" 2>/dev/null
        fi

        echo "[$name] Stopped"
    else
        echo "[$name] Not running (PID $PID not found)"
    fi

    rm -f "$pid_file"
}

echo ""
echo "=========================================="
echo "Dev Log Admin - Stopping Services"
echo "=========================================="
echo ""

case "$TARGET" in
    all)
        stop_service "frontend"
        stop_service "backend"
        stop_service "legacy"
        ;;
    legacy|backend|frontend)
        stop_service "$TARGET"
        ;;
    *)
        echo "Usage: $0 [all|legacy|backend|frontend]"
        exit 1
        ;;
esac

echo ""
