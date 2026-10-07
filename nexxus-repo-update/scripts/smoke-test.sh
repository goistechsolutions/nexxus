#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$ROOT/scripts/validate-package.sh" "$ROOT"
systemd-analyze verify "$ROOT/systemd/nexxus-api.service" "$ROOT/systemd/nexxus-worker.service"
[[ ! -x $ROOT/backend/.venv/bin/pytest ]] || "$ROOT/backend/.venv/bin/pytest" -q "$ROOT/backend/tests"
echo '[OK] Smoke test concluído'
