#!/usr/bin/env bash
set -Eeuo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Execute como root' >&2; exit 1; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; VERSION=${VERSION:-$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || date -u +%Y%m%dT%H%M%SZ)}
"$ROOT/scripts/validate-package.sh" "$ROOT"; "$ROOT/scripts/host-preflight.sh"
id nexxus >/dev/null 2>&1 || useradd --system --home /var/lib/nexxus --shell /usr/sbin/nologin nexxus
install -d -o nexxus -g nexxus -m 0750 /var/lib/nexxus /var/log/nexxus
install -d -m 0750 /etc/nexxus /opt/nexxus/releases
release=/opt/nexxus/releases/$VERSION; [[ ! -e $release ]] || { echo "Release existe: $release" >&2; exit 1; }
cp -a "$ROOT" "$release"; chown -R root:root "$release"; chmod -R go-w "$release"
python3 -m venv "$release/backend/.venv"; "$release/backend/.venv/bin/pip" install --no-cache-dir "$release/backend"
[[ -f /etc/nexxus/api.env ]] || install -m 0640 -o root -g nexxus "$ROOT/config/api.env.example" /etc/nexxus/api.env
[[ -f /etc/nexxus/worker.env ]] || install -m 0640 -o root -g nexxus "$ROOT/config/worker.env.example" /etc/nexxus/worker.env
install -m 0644 "$ROOT/systemd/nexxus-api.service" /etc/systemd/system/
install -m 0644 "$ROOT/systemd/nexxus-worker.service" /etc/systemd/system/
ln -sfn "$release" /opt/nexxus/current
systemctl daemon-reload; systemctl enable nexxus-api.service nexxus-worker.service
echo '[OK] Instalado; revise /etc/nexxus/*.env antes de iniciar.'
