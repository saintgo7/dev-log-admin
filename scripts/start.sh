#!/bin/bash
#
# Dev Log Admin - Unified Start Script
# Usage: ./scripts/start.sh [all|legacy|backend|frontend] [--no-legacy]
#

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PIDS_DIR="$PROJECT_DIR/.pids"
LOGS_DIR="$PROJECT_DIR/.logs"

LEGACY_PORT=8100
BACKEND_PORT=8200
FRONTEND_PORT=3000

mkdir -p "$PIDS_DIR" "$LOGS_DIR"

# Parse arguments
TARGET="${1:-all}"
NO_LEGACY=false
for arg in "$@"; do
    if [ "$arg" = "--no-legacy" ]; then
        NO_LEGACY=true
        TARGET="all"
    fi
done

start_legacy() {
    echo "[Legacy] Starting on port $LEGACY_PORT..."

    if [ -f "$PIDS_DIR/legacy.pid" ]; then
        PID=$(cat "$PIDS_DIR/legacy.pid")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "[Legacy] Already running (PID: $PID)"
            return 0
        fi
        rm -f "$PIDS_DIR/legacy.pid"
    fi

    if lsof -Pi :"$LEGACY_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "[Legacy] Port $LEGACY_PORT already in use"
        return 1
    fi

    if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
        echo "[Legacy] Installing dependencies..."
        pip3 install fastapi uvicorn
    fi

    nohup python3 "$PROJECT_DIR/legacy/server.py" > "$LOGS_DIR/legacy.log" 2>&1 &
    echo $! > "$PIDS_DIR/legacy.pid"
    echo "[Legacy] Started (PID: $!)"
}

start_backend() {
    echo "[Backend] Starting on port $BACKEND_PORT..."

    if [ -f "$PIDS_DIR/backend.pid" ]; then
        PID=$(cat "$PIDS_DIR/backend.pid")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "[Backend] Already running (PID: $PID)"
            return 0
        fi
        rm -f "$PIDS_DIR/backend.pid"
    fi

    if lsof -Pi :"$BACKEND_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "[Backend] Port $BACKEND_PORT already in use"
        return 1
    fi

    cd "$PROJECT_DIR/backend"

    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi

    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" > "$LOGS_DIR/backend.log" 2>&1 &
    echo $! > "$PIDS_DIR/backend.pid"
    echo "[Backend] Started (PID: $!)"

    cd "$PROJECT_DIR"
}

start_frontend() {
    echo "[Frontend] Starting on port $FRONTEND_PORT..."

    if [ -f "$PIDS_DIR/frontend.pid" ]; then
        PID=$(cat "$PIDS_DIR/frontend.pid")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "[Frontend] Already running (PID: $PID)"
            return 0
        fi
        rm -f "$PIDS_DIR/frontend.pid"
    fi

    if lsof -Pi :"$FRONTEND_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "[Frontend] Port $FRONTEND_PORT already in use"
        return 1
    fi

    cd "$PROJECT_DIR/frontend"

    if [ ! -d "node_modules" ]; then
        echo "[Frontend] Installing dependencies..."
        npm install
    fi

    nohup npm run dev > "$LOGS_DIR/frontend.log" 2>&1 &
    echo $! > "$PIDS_DIR/frontend.pid"
    echo "[Frontend] Started (PID: $!)"

    cd "$PROJECT_DIR"
}

echo ""
echo "=========================================="
echo "Dev Log Admin - Starting Services"
echo "=========================================="
echo ""

case "$TARGET" in
    all)
        if [ "$NO_LEGACY" = false ]; then
            start_legacy
        fi
        start_backend
        start_frontend
        ;;
    legacy)
        start_legacy
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    *)
        echo "Usage: $0 [all|legacy|backend|frontend] [--no-legacy]"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Services:"
if [ "$NO_LEGACY" = false ] && [ "$TARGET" = "all" -o "$TARGET" = "legacy" ]; then
    echo "  Legacy:   http://localhost:$LEGACY_PORT"
fi
if [ "$TARGET" = "all" -o "$TARGET" = "backend" ]; then
    echo "  Backend:  http://localhost:$BACKEND_PORT"
    echo "  API Docs: http://localhost:$BACKEND_PORT/docs"
fi
if [ "$TARGET" = "all" -o "$TARGET" = "frontend" ]; then
    echo "  Frontend: http://localhost:$FRONTEND_PORT"
fi
echo "=========================================="
echo ""
echo "Logs: $LOGS_DIR/"
echo "Stop: ./scripts/stop.sh"
echo ""
