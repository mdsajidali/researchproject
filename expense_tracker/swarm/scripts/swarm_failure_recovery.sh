#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# This assumes your Swarm service is called "expense_tracker_web".
# If the name is different, change SERVICE_NAME below.
SERVICE_NAME="${SERVICE_NAME:-expense_tracker_web}"

# Kill one running task of the service to let Swarm reschedule it.
FAILURE_CMD=${FAILURE_CMD:-"docker ps --filter \"name=${SERVICE_NAME}\" --format \"{{.ID}}\" | head -n1 | xargs -r docker kill"}

python3 scripts/failure_recovery.py \
  --label "swarm_onprem_baseline" \
  --service-url "$SERVICE_URL" \
  --failure-cmd "$FAILURE_CMD" \
  --output-file "analysis/failure_recovery_results.csv"

