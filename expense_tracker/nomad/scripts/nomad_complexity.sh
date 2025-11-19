#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DEPLOY_SECONDS=$(cat nomad/scripts/deploy_time.txt)
CONFIG_LINES=$(wc -l < nomad/jobs/expense.nomad)
MANUAL_STEPS=12
ERROR_COUNT=2
WEIGHT=1.15

python3 scripts/complexity_capture.py \
  --env nomad_onprem \
  --deploy-seconds $DEPLOY_SECONDS \
  --config-lines $CONFIG_LINES \
  --manual-steps $MANUAL_STEPS \
  --error-count $ERROR_COUNT \
  --tool-weight $WEIGHT

