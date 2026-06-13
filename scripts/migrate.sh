#!/bin/bash
#
# Dev Log Admin - SQLite to PostgreSQL Migration
# Usage: ./scripts/migrate.sh [--dry-run]
#

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SQLITE_PATH="$PROJECT_DIR/legacy/devlog.db"

echo ""
echo "=========================================="
echo "SQLite -> PostgreSQL Migration"
echo "=========================================="
echo ""

if [ ! -f "$SQLITE_PATH" ]; then
    echo "ERROR: SQLite database not found: $SQLITE_PATH"
    exit 1
fi

cd "$PROJECT_DIR/backend"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 -m scripts.migrate_sqlite_to_postgres \
    --sqlite-path "$SQLITE_PATH" \
    "$@"
