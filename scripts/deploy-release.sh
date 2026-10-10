#!/usr/bin/env bash
set -e
REL=$1
ln -sfn /opt/copilot/releases/$REL /opt/copilot/current
systemctl daemon-reload
systemctl restart copilot-api
systemctl restart copilot-worker
