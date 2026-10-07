#!/usr/bin/env bash
set -Eeuo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || exit 1
systemctl disable --now nexxus-api.service nexxus-worker.service 2>/dev/null || true
rm -f /etc/systemd/system/nexxus-api.service /etc/systemd/system/nexxus-worker.service /opt/nexxus/current
systemctl daemon-reload
if [[ ${1:-} == --confirm-purge && ${2:-} == NEXXUS ]]; then rm -rf /opt/nexxus /etc/nexxus /var/lib/nexxus /var/log/nexxus; userdel nexxus 2>/dev/null || true; fi
echo '[OK] Desinstalação concluída'
