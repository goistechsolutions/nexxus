#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
PGDATABASE=${PGDATABASE:-nexxus}; PGUSER=${PGUSER:-nexxus}; BACKUP_DIR=${BACKUP_DIR:-/var/backups/nexxus}; RETENTION_DAYS=${RETENTION_DAYS:-14}
install -d -m 0700 "$BACKUP_DIR"; exec 9>"$BACKUP_DIR/.backup.lock"; flock -n 9 || { echo 'Backup já em execução' >&2; exit 1; }
stamp=$(date -u +%Y%m%dT%H%M%SZ); out="$BACKUP_DIR/$PGDATABASE-$stamp.dump"; tmp="$out.tmp"; trap 'rm -f "$tmp"' EXIT
pg_dump -Fc -U "$PGUSER" -d "$PGDATABASE" -f "$tmp"; pg_restore --list "$tmp" >/dev/null; mv "$tmp" "$out"; sha256sum "$out" > "$out.sha256"
find "$BACKUP_DIR" -type f \( -name '*.dump' -o -name '*.dump.sha256' \) -mtime "+$RETENTION_DAYS" -delete
echo "[OK] $out"
