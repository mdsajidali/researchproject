#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DEPLOY_SECONDS=$(cat k8s/scripts/deploy_time.txt)
CONFIG_LINES=$(wc -l < k8s/deployment/k8s-deployment.yaml)
MANUAL_STEPS=8        # fixed for your implementation
ERROR_COUNT=1         # minor retries
WEIGHT=1.0

python3 scripts/complexity_capture.py \
  --env k8s_onprem \
  --deploy-seconds $DEPLOY_SECONDS \
  --config-lines $CONFIG_LINES \
  --manual-steps $MANUAL_STEPS \
  --error-count $ERROR_COUNT \
  --tool-weight $WEIGHT

