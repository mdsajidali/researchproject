#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# Nomad job name for the web app
NOMAD_JOB_NAME="${NOMAD_JOB_NAME:-expense-tracker}"

# Restart the job (simulate failure + reschedule)
FAILURE_CMD=${FAILURE_CMD:-"nomad job restart ${NOMAD_JOB_NAME}"}

python3 scripts/failure_recovery.py \
  --label "nomad_onprem_baseline" \
  --service-url "$SERVICE_URL" \
  --failure-cmd "$FAILURE_CMD" \
  --output-file "analysis/failure_recovery_results.csv"

