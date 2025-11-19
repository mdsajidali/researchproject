#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DEPLOY_SECONDS=$(cat swarm/scripts/deploy_time.txt)
CONFIG_LINES=$(wc -l < swarm/docker-stack.yml)
MANUAL_STEPS=5
ERROR_COUNT=0
WEIGHT=0.85

python3 scripts/complexity_capture.py \
  --env swarm_onprem \
  --deploy-seconds $DEPLOY_SECONDS \
  --config-lines $CONFIG_LINES \
  --manual-steps $MANUAL_STEPS \
  --error-count $ERROR_COUNT \
  --tool-weight $WEIGHT

