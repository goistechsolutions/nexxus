#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}; failures=0
required=(backend/pyproject.toml backend/app/main.py backend/alembic.ini backend/migrations/env.py systemd/nexxus-api.service systemd/nexxus-worker.service config/api.env.example config/worker.env.example)
for f in "${required[@]}"; do [[ -f $ROOT/$f ]] || { echo "[FAIL] $f" >&2; failures=$((failures+1)); }; done
for s in "$ROOT"/scripts/*.sh; do bash -n "$s" || failures=$((failures+1)); done
python3 -m compileall -q "$ROOT/backend/app" "$ROOT/backend/migrations" || failures=$((failures+1))
validate_systemd_syntax() {
local unit="$1"
 
[[ -f "$unit" ]] || {
echo "[FAIL] Unit ausente: $unit" >&2
return 1
}
 
grep -q '^\[Unit\]$' "$unit" || {
echo "[FAIL] Seção [Unit] ausente: $unit" >&2
return 1
}
 
grep -q '^\[Service\]$' "$unit" || {
echo "[FAIL] Seção [Service] ausente: $unit" >&2
return 1
}
 
grep -q '^ExecStart=' "$unit" || {
echo "[FAIL] ExecStart ausente: $unit" >&2
return 1
}
 
echo "[OK] Estrutura da unit válida: ${unit#"$ROOT/"}"
}
 
validate_systemd_syntax "$ROOT/systemd/nexxus-api.service" ||
failures=$((failures + 1))
 
if [[ -d "$ROOT/worker" ]]; then
validate_systemd_syntax "$ROOT/systemd/nexxus-worker.service" ||
failures=$((failures + 1))
else
echo "[WARN] Worker não publicado; validação da unit ignorada."
fi
grep -RIlE 'REPLACE_WITH_SECRET_MANAGER_VALUE' "$ROOT" --exclude='*.example' --exclude='validate-package.sh' | grep . && { echo '[FAIL] placeholder fora de exemplo' >&2; failures=$((failures+1)); } || true
((failures==0)) || exit 1
echo '[OK] Pacote válido'
