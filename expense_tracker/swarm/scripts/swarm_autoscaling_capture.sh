#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

SERVICE_IMAGE="${SERVICE_IMAGE:-docker.io/mdsajidali/expense-tracker:1.1}"

# Count containers running from the app image
REPLICA_CMD=${REPLICA_CMD:-"docker ps --filter ancestor=${SERVICE_IMAGE} --format '{{.ID}}' | wc -l"}

LOAD_CMD="${LOAD_CMD:-}"

EXTRA_ARGS=()
if [ -n "${LOAD_CMD}" ]; then
  EXTRA_ARGS+=(--load-cmd "${LOAD_CMD}")
fi

python3 scripts/autoscaling_capture.py \
  --label "swarm_onprem_spike" \
  --service-url "${SERVICE_URL}" \
  --replica-cmd "${REPLICA_CMD}" \
  --output-file "analysis/autoscaling_results.csv" \
  "${EXTRA_ARGS[@]}"

