#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# Project/namespace and selector for the web app
OS_PROJECT="${OS_PROJECT:-expense}"
OS_SELECTOR="${OS_SELECTOR:-app=expense-tracker}"

FAILURE_CMD=${FAILURE_CMD:-"oc -n ${OS_PROJECT} delete pod -l ${OS_SELECTOR} --wait=false"}

python3 scripts/failure_recovery.py \
  --label "microshift_onprem_baseline" \
  --service-url "$SERVICE_URL" \
  --failure-cmd "$FAILURE_CMD" \
  --output-file "analysis/failure_recovery_results.csv"

