#!/usr/bin/env bash
set -e
PREV=$1
ln -sfn /opt/copilot/releases/$PREV /opt/copilot/current
systemctl restart copilot-api copilot-worker
