#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# Default assumes a Swarm stack file at swarm/docker-compose.yml
# and stack name "expense_tracker".
DEPLOY_CMD="${DEPLOY_CMD:-docker stack deploy -c swarm/docker-compose.yml expense_tracker}"

python3 scripts/deployment_time_capture.py \
  --label "swarm_onprem_deploy" \
  --service-url "${SERVICE_URL}" \
  --deploy-cmd "${DEPLOY_CMD}" \
  --output-file "analysis/deployment_time_results.csv"

