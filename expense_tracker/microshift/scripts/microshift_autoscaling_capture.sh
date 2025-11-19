#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# Count ready replicas of the expense-tracker deployment in edge-demo
REPLICA_CMD=${REPLICA_CMD:-"oc -n edge-demo get deploy expense-tracker -o yaml | awk '/readyReplicas/ {print \$2; exit}'"}

LOAD_CMD="${LOAD_CMD:-}"

EXTRA_ARGS=()
if [ -n "${LOAD_CMD}" ]; then
  EXTRA_ARGS+=(--load-cmd "${LOAD_CMD}")
fi

python3 scripts/autoscaling_capture.py \
  --label "microshift_cloud_spike" \
  --service-url "${SERVICE_URL}" \
  --replica-cmd "${REPLICA_CMD}" \
  --output-file "analysis/autoscaling_results.csv" \
  "${EXTRA_ARGS[@]}"

