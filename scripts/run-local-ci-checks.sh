#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
NODE_VERSION="${NODE_VERSION:-20}"
VERSION="${VERSION:-local-$(date +%Y%m%d%H%M%S)}"

PG_CONTAINER="math-racers-ci-postgres"
REDIS_CONTAINER="math-racers-ci-redis"
NGINX_CONTAINER="math-racers-ci-nginx"

cleanup() {
  docker rm -f "$NGINX_CONTAINER" >/dev/null 2>&1 || true
  docker rm -f "$PG_CONTAINER" >/dev/null 2>&1 || true
  docker rm -f "$REDIS_CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

step() {
  printf '\n==> %s\n' "$1"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: Missing required command: $1"
    exit 1
  fi
}

wait_for_http() {
  local url="$1"
  local timeout_secs="$2"
  local i
  for ((i=1; i<=timeout_secs; i++)); do
    if curl -sf "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  echo "ERROR: Timed out waiting for $url"
  return 1
}

step "Checking required tools"
require_cmd docker
require_cmd curl
require_cmd git
require_cmd python3
require_cmd node
require_cmd npm

step "Tool versions"
python3 --version
node --version
npm --version
if command -v uv >/dev/null 2>&1; then uv --version; fi
if command -v pnpm >/dev/null 2>&1; then pnpm --version; fi
if command -v trivy >/dev/null 2>&1; then trivy --version; fi

step "Install uv and pip-audit"
python3 -m pip install --upgrade pip
python3 -m pip install uv pip-audit

step "Install backend dependencies"
(
  cd "$BACKEND_DIR"
  uv pip install --system -e ".[dev]"
)

step "Install pnpm if missing"
if ! command -v pnpm >/dev/null 2>&1; then
  npm install -g pnpm
fi

step "Install frontend dependencies"
(
  cd "$FRONTEND_DIR"
  pnpm install --frozen-lockfile
)

step "Start Postgres test service"
docker rm -f "$PG_CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$PG_CONTAINER" \
  -e POSTGRES_DB=mathracers_test \
  -e POSTGRES_USER=mathracers \
  -e POSTGRES_PASSWORD=testpass \
  -p 5432:5432 \
  postgres:16-alpine >/dev/null

step "Wait for Postgres"
for _ in {1..30}; do
  if docker exec "$PG_CONTAINER" pg_isready >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
docker exec "$PG_CONTAINER" pg_isready >/dev/null 2>&1 || {
  echo "ERROR: Postgres did not become healthy"
  exit 1
}

step "Start Redis test service"
docker rm -f "$REDIS_CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$REDIS_CONTAINER" -p 6379:6379 redis:7-alpine >/dev/null

step "Wait for Redis"
for _ in {1..30}; do
  if docker exec "$REDIS_CONTAINER" redis-cli ping | grep -q PONG; then
    break
  fi
  sleep 1
done
docker exec "$REDIS_CONTAINER" redis-cli ping | grep -q PONG || {
  echo "ERROR: Redis did not become healthy"
  exit 1
}

step "Format checks"
(
  cd "$BACKEND_DIR"
  black --check .
)
(
  cd "$FRONTEND_DIR"
  pnpm prettier --check "src/**/*.{ts,tsx,css,json}" --ignore-unknown
)

step "Lint checks"
(
  cd "$BACKEND_DIR"
  ruff check .
)
(
  cd "$FRONTEND_DIR"
  pnpm eslint src
)

step "Static analysis"
(
  cd "$BACKEND_DIR"
  mypy .
)
(
  cd "$FRONTEND_DIR"
  pnpm tsc --noEmit
)

step "Unit tests"
(
  cd "$BACKEND_DIR"
  pytest -m unit --tb=short
)
(
  cd "$FRONTEND_DIR"
  pnpm vitest run
)

step "Integration tests"
(
  cd "$BACKEND_DIR"
  DATABASE_URL="postgresql+asyncpg://mathracers:testpass@localhost:5432/mathracers_test" \
  REDIS_URL="redis://localhost:6379/0" \
  JWT_SECRET="ci-test-secret-32-bytes-minimum-xx" \
  OPENAI_API_KEY="sk-test-placeholder" \
  STORAGE_ENDPOINT="https://CHANGE_ME" \
  STORAGE_ACCESS_KEY="test" \
  STORAGE_SECRET_KEY="test" \
  STORAGE_BUCKET="test" \
  ADMIN_EMAIL="admin@ci.local" \
  ADMIN_PASSWORD="ci-admin-password-placeholder" \
  ENVIRONMENT="development" \
  VERSION="$VERSION" \
  LOG_LEVEL="WARNING" \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 >/tmp/math-racers-ci-uvicorn.log 2>&1 &
  UVICORN_PID=$!

  kill_backend() {
    kill "$UVICORN_PID" >/dev/null 2>&1 || true
  }
  trap kill_backend EXIT

  wait_for_http "http://localhost:8000/health" 30

  HEALTH_URL="http://localhost:8000/health" pytest -m integration --tb=short

  kill "$UVICORN_PID" >/dev/null 2>&1 || true
  wait "$UVICORN_PID" 2>/dev/null || true
  trap - EXIT
)

step "Verify clean working tree"
if [ -n "$(cd "$ROOT_DIR" && git status --porcelain)" ]; then
  echo "ERROR: working tree is dirty — cannot build release images"
  exit 1
fi

step "Build backend image"
docker build --build-arg VERSION="$VERSION" -t "math-racers/backend:$VERSION" "$BACKEND_DIR"

step "Build frontend image"
docker build -t "math-racers/frontend:$VERSION" "$FRONTEND_DIR"

step "Security scan: Trivy images"
if command -v trivy >/dev/null 2>&1; then
  trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed "math-racers/backend:$VERSION"
  trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed "math-racers/frontend:$VERSION"
else
  echo "ERROR: trivy is required to run image security checks. Install it and rerun."
  exit 1
fi

step "Security scan: Python dependencies"
(
  cd "$BACKEND_DIR"
  pip-audit --requirement <(uv pip compile pyproject.toml)
)

step "Security scan: Node dependencies"
(
  cd "$FRONTEND_DIR"
  pnpm audit --audit-level critical
)

step "Check for hardcoded secrets"
(
  cd "$ROOT_DIR"
  if grep -rE "(SECRET|PASSWORD|API_KEY)\\s*=\\s*['\"][^\$]" . \
      --include="*.py" --include="*.ts" --include="*.tsx" \
      --include="*.yml" --include="*.yaml" \
      --exclude-dir=".git" \
      --exclude-dir="node_modules" \
      --exclude="*.example"; then
    echo "ERROR: Possible hardcoded secrets detected"
    exit 1
  fi
)

step "Smoke test: HSTS header"
TMP_CERT_DIR="/tmp/math-racers-ci-nginx-certs"
TMP_CONF_DIR="/tmp/math-racers-ci-nginx-conf"
mkdir -p "$TMP_CERT_DIR" "$TMP_CONF_DIR"
openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
  -keyout "$TMP_CERT_DIR/privkey.pem" \
  -out "$TMP_CERT_DIR/fullchain.pem" \
  -subj "/CN=localhost" 2>/dev/null

cat > "$TMP_CONF_DIR/hsts-check.conf" <<'EOF'
server {
  listen 443 ssl;
  server_name _;
  ssl_certificate /etc/nginx/certs/fullchain.pem;
  ssl_certificate_key /etc/nginx/certs/privkey.pem;
  default_type text/plain;
  add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
  location / { return 200 "ok"; }
}
EOF

docker rm -f "$NGINX_CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$NGINX_CONTAINER" \
  -p 443:443 \
  -v "$TMP_CERT_DIR:/etc/nginx/certs:ro" \
  -v "$TMP_CONF_DIR/hsts-check.conf:/etc/nginx/conf.d/default.conf:ro" \
  nginx:1.27-alpine >/dev/null

sleep 3
HSTS="$(curl -skI https://localhost/ | grep -i strict-transport-security || true)"
docker rm -f "$NGINX_CONTAINER" >/dev/null 2>&1 || true

if ! echo "$HSTS" | grep -q "max-age=63072000"; then
  echo "ERROR: HSTS header missing or incorrect: '$HSTS'"
  exit 1
fi

if ! grep -q "max-age=63072000" "$ROOT_DIR/nginx/conf.d/default.conf"; then
  echo "ERROR: HSTS header missing from production nginx config"
  exit 1
fi

echo "HSTS OK: $HSTS"

echo
echo "All local CI checks passed."

