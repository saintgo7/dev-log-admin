#!/bin/bash
#
# Dev Log Admin - Service Status
#

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PIDS_DIR="$PROJECT_DIR/.pids"

LEGACY_PORT=8100
BACKEND_PORT=8200
FRONTEND_PORT=3000

check_service() {
    local name="$1"
    local port="$2"
    local pid_file="$PIDS_DIR/$name.pid"

    printf "%-12s" "[$name]"

    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p "$PID" > /dev/null 2>&1; then
            MEM=$(ps -o rss= -p "$PID" 2>/dev/null | awk '{printf "%.1f MB", $1/1024}')
            printf "RUNNING  PID: %-8s Port: %-6s Mem: %s\n" "$PID" "$port" "$MEM"
            return 0
        else
            rm -f "$pid_file"
            printf "DEAD     (stale PID file removed)\n"
            return 1
        fi
    else
        if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
            PROC_PID=$(lsof -ti:"$port" 2>/dev/null)
            printf "UNKNOWN  Port $port in use by PID: $PROC_PID\n"
            return 2
        fi
        printf "STOPPED\n"
        return 1
    fi
}

echo ""
echo "=========================================="
echo "Dev Log Admin - Service Status"
echo "=========================================="
echo ""

check_service "legacy" "$LEGACY_PORT"
check_service "backend" "$BACKEND_PORT"
check_service "frontend" "$FRONTEND_PORT"

echo ""
echo "------------------------------------------"
echo "Database:"

# SQLite
if [ -f "$PROJECT_DIR/legacy/devlog.db" ]; then
    SIZE=$(ls -lh "$PROJECT_DIR/legacy/devlog.db" | awk '{print $5}')
    PROJECTS=$(python3 -c "import sqlite3; c=sqlite3.connect('$PROJECT_DIR/legacy/devlog.db'); print(c.execute('SELECT COUNT(*) FROM projects').fetchone()[0])" 2>/dev/null || echo "?")
    COMMITS=$(python3 -c "import sqlite3; c=sqlite3.connect('$PROJECT_DIR/legacy/devlog.db'); print(c.execute('SELECT COUNT(*) FROM commits').fetchone()[0])" 2>/dev/null || echo "?")
    echo "  SQLite:     $SIZE ($PROJECTS projects, $COMMITS commits)"
else
    echo "  SQLite:     not found"
fi

# PostgreSQL
if command -v psql &> /dev/null; then
    PG_STATUS=$(psql -d devlog -c "SELECT COUNT(*) FROM projects" -t 2>/dev/null | tr -d ' ')
    if [ -n "$PG_STATUS" ]; then
        PG_COMMITS=$(psql -d devlog -c "SELECT COUNT(*) FROM commits" -t 2>/dev/null | tr -d ' ')
        echo "  PostgreSQL: connected ($PG_STATUS projects, $PG_COMMITS commits)"
    else
        echo "  PostgreSQL: not available"
    fi
else
    echo "  PostgreSQL: psql not installed"
fi

echo ""
