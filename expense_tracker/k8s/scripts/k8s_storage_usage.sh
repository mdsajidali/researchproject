#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Node usage (root filesystem)
NODE_CMD="df -m / | tail -1 | awk '{print \$3}'"

# Container usage: get container filesystem size
POD_NAME=$(kubectl -n expense get pod -l app=expense-tracker -o jsonpath='{.items[0].metadata.name}')
CONTAINER_CMD="kubectl -n expense exec ${POD_NAME} -- du -sm /app | awk '{print \$1}'"

# PV Usage (optional)
PV_CMD="kubectl -n expense exec ${POD_NAME} -- du -sm /data | awk '{print \$1}'"

python3 scripts/storage_usage_capture.py \
  --label "k8s_onprem_storage" \
  --node-cmd "$NODE_CMD" \
  --container-cmd "$CONTAINER_CMD" \
  --pv-cmd "$PV_CMD"

