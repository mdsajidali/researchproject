#!/usr/bin/env bash
set -euo pipefail

# Move to expense_tracker root (where scripts/ lives)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

# URL where the app is reachable in your k8s environment
SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# Command that injects a failure for the web app.
# Adjust namespace / selector to match your deployment if needed.
FAILURE_CMD="${FAILURE_CMD:-kubectl -n expense delete pod -l app=expense-tracker --wait=false}"

python3 scripts/failure_recovery.py \
  --label "k8s_onprem_baseline" \
  --service-url "$SERVICE_URL" \
  --failure-cmd "$FAILURE_CMD" \
  --output-file "analysis/failure_recovery_results.csv"

