#!/usr/bin/env bash
set -e
apt update
apt full-upgrade -y
apt install -y nginx python3 python3-venv python3-pip python3-dev build-essential libpq-dev postgresql
useradd --system --home /opt/copilot --create-home --shell /usr/sbin/nologin copilot || true
mkdir -p /opt/copilot/releases /opt/copilot/shared /etc/copilot /var/log/copilot /var/backups/copilot
