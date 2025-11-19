#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# Default assumes Nomad job file nomad/expense-tracker.nomad
NOMAD_JOB_FILE="${NOMAD_JOB_FILE:-nomad/expense-tracker.nomad}"
DEPLOY_CMD="${DEPLOY_CMD:-nomad job run ${NOMAD_JOB_FILE}}"

python3 scripts/deployment_time_capture.py \
  --label "nomad_onprem_deploy" \
  --service-url "${SERVICE_URL}" \
  --deploy-cmd "${DEPLOY_CMD}" \
  --output-file "analysis/deployment_time_results.csv"

