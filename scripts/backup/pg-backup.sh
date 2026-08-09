#!/usr/bin/env bash
# Daily PostgreSQL backup: dump, manifest, upload to object storage, prune old backups.
# Exits non-zero on any failure.

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/mathracers}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
BACKUP_ID=$(python3 -c "import uuid; print(uuid.uuid4())")
FILENAME="pg-backup-${TIMESTAMP}.dump.gz"
FILEPATH="${BACKUP_DIR}/${FILENAME}"

mkdir -p "$BACKUP_DIR"

echo "[backup] Starting PostgreSQL backup (id=${BACKUP_ID})"

# Require env vars
: "${DATABASE_URL:?DATABASE_URL must be set}"
: "${STORAGE_ENDPOINT:?STORAGE_ENDPOINT must be set}"
: "${STORAGE_ACCESS_KEY:?STORAGE_ACCESS_KEY must be set}"
: "${STORAGE_SECRET_KEY:?STORAGE_SECRET_KEY must be set}"
: "${STORAGE_BUCKET:?STORAGE_BUCKET must be set}"

# Extract connection details from DATABASE_URL (asyncpg → psycopg2 format for pg_dump)
# Expected format: postgresql+asyncpg://user:pass@host:port/dbname
PG_URL="${DATABASE_URL/postgresql+asyncpg/postgresql}"

# Dump
echo "[backup] Running pg_dump..."
pg_dump --format=custom "$PG_URL" | gzip > "$FILEPATH"
echo "[backup] Dump complete: $FILEPATH"

# Checksum
CHECKSUM=$(sha256sum "$FILEPATH" | awk '{print $1}')
PG_VERSION=$(psql "$PG_URL" -tAc "SELECT version();" 2>/dev/null || echo "unknown")

# Write manifest
MANIFEST_PATH="${FILEPATH%.gz}.manifest.json"
python3 - <<EOF
import json
manifest = {
    "backup_id": "${BACKUP_ID}",
    "created_at": "${TIMESTAMP}",
    "type": "full_dump",
    "source_host": "$(hostname)",
    "pg_version": "${PG_VERSION}",
    "file_path": "${FILENAME}",
    "checksum_sha256": "${CHECKSUM}",
}
with open("${MANIFEST_PATH}", "w") as f:
    json.dump(manifest, f, indent=2)
print("[backup] Manifest written:", "${MANIFEST_PATH}")
EOF

# Upload to object storage (AWS CLI compatible; works with S3 and S3-compatible stores)
AWS_ACCESS_KEY_ID="$STORAGE_ACCESS_KEY" \
AWS_SECRET_ACCESS_KEY="$STORAGE_SECRET_KEY" \
aws s3 cp "$FILEPATH" "s3://${STORAGE_BUCKET}/backups/${FILENAME}" \
    --endpoint-url "$STORAGE_ENDPOINT"

AWS_ACCESS_KEY_ID="$STORAGE_ACCESS_KEY" \
AWS_SECRET_ACCESS_KEY="$STORAGE_SECRET_KEY" \
aws s3 cp "$MANIFEST_PATH" "s3://${STORAGE_BUCKET}/backups/$(basename "$MANIFEST_PATH")" \
    --endpoint-url "$STORAGE_ENDPOINT"

echo "[backup] Uploaded to s3://${STORAGE_BUCKET}/backups/"

# Prune local files older than retention period
find "$BACKUP_DIR" -name "pg-backup-*.dump.gz" -mtime +"$RETENTION_DAYS" -delete
find "$BACKUP_DIR" -name "*.manifest.json" -mtime +"$RETENTION_DAYS" -delete
echo "[backup] Pruned local backups older than ${RETENTION_DAYS} days"

echo "[backup] Backup complete (id=${BACKUP_ID})"
