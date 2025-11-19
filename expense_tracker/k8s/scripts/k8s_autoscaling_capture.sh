#!/usr/bin/env bash
set -euo pipefail

# Root of the Django project (where manage.py and scripts/ live)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# Replica count via kubectl: read readyReplicas from YAML
REPLICA_CMD=${REPLICA_CMD:-"kubectl -n expense get deploy expense-web -o yaml | awk '/readyReplicas/ {print \$2; exit}'"}

# Optional: JMeter load generator command.
# Leave LOAD_CMD empty if you prefer to run JMeter manually in another terminal.
LOAD_CMD="${LOAD_CMD:-}"

EXTRA_ARGS=()
if [ -n "${LOAD_CMD}" ]; then
  EXTRA_ARGS+=(--load-cmd "${LOAD_CMD}")
fi

python3 scripts/autoscaling_capture.py \
  --label "k8s_onprem_spike" \
  --service-url "${SERVICE_URL}" \
  --replica-cmd "${REPLICA_CMD}" \
  --output-file "analysis/autoscaling_results.csv" \
  "${EXTRA_ARGS[@]}"

