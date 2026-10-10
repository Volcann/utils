#!/usr/bin/env bash
set -euo pipefail

UTILS_DIR="$(cd "$(dirname "$0")" && pwd)"
DJANGO_DIR="/home/folium/Documents/volcanai"
DJANGO_VENV="$DJANGO_DIR/.venv/bin/python"

pids=()

cleanup() {
    echo ""
    echo "Stopping all services..."
    for pid in "${pids[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
    echo "Done."
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Starting Django..."
cd "$DJANGO_DIR"
"$DJANGO_VENV" manage.py runserver 0.0.0.0:8000 &
pids+=($!)
echo "  Django PID: ${pids[-1]}"

echo ""
echo "  Django  → http://localhost:8000"
echo ""
echo "  Press Ctrl+C to stop all."
echo ""

wait
