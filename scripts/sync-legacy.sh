#!/bin/bash
#
# Dev Log Admin - Legacy Sync (JSON -> SQLite)
# Usage: ./scripts/sync-legacy.sh [--discover]
#

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo ""
echo "=========================================="
echo "Legacy Sync"
echo "=========================================="
echo ""

# Auto-discover if requested
if [ "$1" = "--discover" ]; then
    echo "Running auto-discover..."
    python3 "$PROJECT_DIR/legacy/auto-discover.py" --yes
    echo ""
fi

# Sync to SQLite
echo "Syncing to SQLite..."
python3 "$PROJECT_DIR/legacy/sync.py"
