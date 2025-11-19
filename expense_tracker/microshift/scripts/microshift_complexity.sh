#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DEPLOY_SECONDS=$(cat microshift/scripts/deploy_time.txt)
CONFIG_LINES=$(wc -l < microshift/manifests/app.yaml)
MANUAL_STEPS=15
ERROR_COUNT=3
WEIGHT=1.3

python3 scripts/complexity_capture.py \
  --env microshift_cloud \
  --deploy-seconds $DEPLOY_SECONDS \
  --config-lines $CONFIG_LINES \
  --manual-steps $MANUAL_STEPS \
  --error-count $ERROR_COUNT \
  --tool-weight $WEIGHT

