#!/usr/bin/env bash
set -Eeuo pipefail
API_SERVICE=${API_SERVICE:-nexxus-api.service}; WORKER_SERVICE=${WORKER_SERVICE:-nexxus-worker.service}
LIVE_URL=${LIVE_URL:-http://127.0.0.1:8000/health/live}; READY_URL=${READY_URL:-http://127.0.0.1:8000/health/ready}
PGDATABASE=${PGDATABASE:-nexxus}; PGUSER=${PGUSER:-nexxus}; failures=0
check(){ "$@" >/dev/null 2>&1 || { echo "[FAIL] $*" >&2; failures=$((failures+1)); }; }
check systemctl is-active --quiet "$API_SERVICE"
check systemctl is-active --quiet "$WORKER_SERVICE"
check curl --fail --silent --max-time 10 "$LIVE_URL"
check curl --fail --silent --max-time 10 "$READY_URL"
check pg_isready -d "$PGDATABASE" -U "$PGUSER"
attrs="$(psql -XAt -d "$PGDATABASE" -U "$PGUSER" -c "select rolsuper||':'||rolbypassrls from pg_roles where rolname=current_user" 2>/dev/null || true)"
[[ $attrs == f:f ]] || { echo '[FAIL] role da API não pode ser SUPERUSER/BYPASSRLS' >&2; failures=$((failures+1)); }
((failures==0)) || exit 1
echo '[OK] Health check aprovado'
