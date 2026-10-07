#!/usr/bin/env bash
set -Eeuo pipefail
[[ $# -eq 3 && $2 == --confirm-database ]] || { echo "Uso: $0 BACKUP --confirm-database BANCO" >&2; exit 2; }
backup=$1; expected=$3; PGDATABASE=${PGDATABASE:-nexxus}; PGUSER=${PGUSER:-postgres}
[[ $expected == "$PGDATABASE" ]] || { echo 'Confirmação do banco não corresponde' >&2; exit 2; }
[[ -r $backup ]] || exit 1
[[ ! -f $backup.sha256 ]] || (cd "$(dirname "$backup")" && sha256sum -c "$(basename "$backup").sha256")
systemctl is-active --quiet nexxus-api.service && { echo 'Pare a API antes do restore' >&2; exit 1; }
systemctl is-active --quiet nexxus-worker.service && { echo 'Pare o worker antes do restore' >&2; exit 1; }
pg_restore --exit-on-error --clean --if-exists --no-owner --no-privileges -U "$PGUSER" -d "$PGDATABASE" "$backup"
psql -X -U "$PGUSER" -d "$PGDATABASE" -c 'ANALYZE' >/dev/null
echo '[OK] Restore concluído'
