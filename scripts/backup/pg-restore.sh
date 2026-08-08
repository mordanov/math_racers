#!/usr/bin/env bash
# Restore PostgreSQL database from a backup file.
# Usage: ./pg-restore.sh <backup-file.dump.gz> <target-database-name>

set -euo pipefail

BACKUP_FILE="${1:?Usage: $0 <backup-file.dump.gz> <target-db-name>}"
TARGET_DB="${2:?Usage: $0 <backup-file.dump.gz> <target-db-name>}"

: "${DATABASE_URL:?DATABASE_URL must be set}"

PG_URL_BASE="${DATABASE_URL/postgresql+asyncpg/postgresql}"
# Replace database name at the end of the URL
PG_URL_TARGET=$(echo "$PG_URL_BASE" | sed "s|/[^/]*$|/${TARGET_DB}|")

echo "[restore] Starting restore from $BACKUP_FILE to database '$TARGET_DB'"

# Verify checksum if manifest exists
MANIFEST="${BACKUP_FILE%.gz}.manifest.json"
if [ -f "$MANIFEST" ]; then
    EXPECTED=$(python3 -c "import json; d=json.load(open('${MANIFEST}')); print(d['checksum_sha256'])")
    ACTUAL=$(sha256sum "$BACKUP_FILE" | awk '{print $1}')
    if [ "$EXPECTED" != "$ACTUAL" ]; then
        echo "[restore] ERROR: Checksum mismatch — backup file may be corrupt"
        echo "  Expected: $EXPECTED"
        echo "  Actual:   $ACTUAL"
        exit 1
    fi
    echo "[restore] Checksum verified OK"
else
    echo "[restore] WARNING: No manifest found — skipping checksum verification"
fi

# Decompress and restore
echo "[restore] Restoring..."
gunzip -c "$BACKUP_FILE" | pg_restore \
    --dbname="$PG_URL_TARGET" \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges

echo "[restore] SUCCESS — database '$TARGET_DB' restored from $BACKUP_FILE"
