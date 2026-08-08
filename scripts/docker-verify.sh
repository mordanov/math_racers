#!/usr/bin/env bash
# Polls the health endpoint until status=ok or timeout (60s).
# Exits non-zero on timeout.

set -euo pipefail

HEALTH_URL="${HEALTH_URL:-http://localhost/health}"
TIMEOUT=60
INTERVAL=2
elapsed=0

echo "[verify] Waiting for stack to become healthy at $HEALTH_URL..."

while true; do
    status=$(curl -sf "$HEALTH_URL" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null || echo "unreachable")

    if [ "$status" = "ok" ]; then
        echo "[verify] Stack is healthy (status=ok)"
        exit 0
    fi

    if [ "$elapsed" -ge "$TIMEOUT" ]; then
        echo "[verify] ERROR: Stack did not become healthy within ${TIMEOUT}s (last status: $status)"
        exit 1
    fi

    echo "[verify] status=$status — waiting ${INTERVAL}s... (${elapsed}s elapsed)"
    sleep "$INTERVAL"
    elapsed=$((elapsed + INTERVAL))
done
