#!/usr/bin/env bash
# Check TLS certificate expiry from the nginx_certs Docker volume.
# Exits non-zero if certificate expires in < 30 days.
# Use in cron or CI smoke tests.

set -euo pipefail

CERT_PATH="${CERT_PATH:-/etc/nginx/certs/fullchain.pem}"
WARN_DAYS="${WARN_DAYS:-30}"

if [ ! -f "$CERT_PATH" ]; then
    # Try reading from the container
    CERT_CONTENT=$(docker compose exec nginx cat /etc/nginx/certs/fullchain.pem 2>/dev/null || true)
    if [ -z "$CERT_CONTENT" ]; then
        echo "[cert-check] WARNING: Certificate not found at $CERT_PATH and not accessible in container"
        exit 0
    fi
    EXPIRY=$(echo "$CERT_CONTENT" | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
else
    EXPIRY=$(openssl x509 -noout -enddate -in "$CERT_PATH" | cut -d= -f2)
fi

EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))

echo "[cert-check] Certificate expires: $EXPIRY (${DAYS_LEFT} days remaining)"

if [ "$DAYS_LEFT" -lt "$WARN_DAYS" ]; then
    echo "[cert-check] ERROR: Certificate expires in ${DAYS_LEFT} days — renewal required"
    exit 1
fi

echo "[cert-check] OK — certificate valid for ${DAYS_LEFT} more days"
exit 0
