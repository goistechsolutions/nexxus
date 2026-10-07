#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}; failures=0
required=(backend/pyproject.toml backend/app/main.py backend/alembic.ini backend/migrations/env.py systemd/nexxus-api.service systemd/nexxus-worker.service config/api.env.example config/worker.env.example)
for f in "${required[@]}"; do [[ -f $ROOT/$f ]] || { echo "[FAIL] $f" >&2; failures=$((failures+1)); }; done
for s in "$ROOT"/scripts/*.sh; do bash -n "$s" || failures=$((failures+1)); done
python3 -m compileall -q "$ROOT/backend/app" "$ROOT/backend/migrations" || failures=$((failures+1))
command -v systemd-analyze >/dev/null && systemd-analyze verify "$ROOT/systemd/nexxus-api.service" "$ROOT/systemd/nexxus-worker.service" || failures=$((failures+1))
grep -RIlE 'REPLACE_WITH_SECRET_MANAGER_VALUE' "$ROOT" --exclude='*.example' --exclude='validate-package.sh' | grep . && { echo '[FAIL] placeholder fora de exemplo' >&2; failures=$((failures+1)); } || true
((failures==0)) || exit 1
echo '[OK] Pacote válido'
