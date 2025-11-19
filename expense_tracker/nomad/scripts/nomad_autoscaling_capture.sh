#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# Nomad auto-scaling is not configured; this command always returns 1.
REPLICA_CMD=${REPLICA_CMD:-"echo 1"}

LOAD_CMD="${LOAD_CMD:-}"

EXTRA_ARGS=()
if [ -n "${LOAD_CMD}" ]; then
  EXTRA_ARGS+=(--load-cmd "${LOAD_CMD}")
fi

python3 scripts/autoscaling_capture.py \
  --label "nomad_onprem_spike" \
  --service-url "${SERVICE_URL}" \
  --replica-cmd "${REPLICA_CMD}" \
  --output-file "analysis/autoscaling_results.csv" \
  "${EXTRA_ARGS[@]}"

