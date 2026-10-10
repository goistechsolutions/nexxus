#!/usr/bin/env bash
set -Eeuo pipefail
failures=0
ok(){ printf '[OK] %s\n' "$*"; }
fail(){ printf '[FAIL] %s\n' "$*" >&2; failures=$((failures+1)); }
. /etc/os-release
[[ ${ID:-} == ubuntu && ${VERSION_ID:-} == 26.04 && ${VERSION_CODENAME:-} == resolute ]] || fail "Requer Ubuntu 26.04 (resolute)"
for c in systemctl python3 psql pg_isready pg_dump pg_restore curl sha256sum flock; do command -v "$c" >/dev/null || fail "Ausente: $c"; done
python3 - <<'PY' || exit 1
import sys
raise SystemExit(0 if sys.version_info >= (3,12) else 1)
PY
pg_isready >/dev/null 2>&1 || fail 'PostgreSQL indisponível'
if command -v psql >/dev/null; then
 major="$(psql -XAtqc 'show server_version_num' postgres 2>/dev/null | cut -c1-2 || true)"
 [[ $major =~ ^[0-9]+$ && $major -ge 16 ]] || fail 'PostgreSQL servidor deve ser 16+'
 [[ "$(psql -XAtqc "select exists(select 1 from pg_extension where extname='vector')" postgres 2>/dev/null || true)" == t ]] || fail 'pgvector ausente'
fi
((failures==0)) || exit 1
ok 'Preflight aprovado'
