#!/usr/bin/env bash
set -euo pipefail

# Go to expense_tracker root (where scripts/ and manage.py live)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

# URL where the app is reachable in this environment
SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# Command that deploys the k8s resources.
# Default assumes all manifests are under k8s/.
# If you use a different layout, override DEPLOY_CMD when running.
DEPLOY_CMD="${DEPLOY_CMD:-kubectl apply -f k8s/}"

python3 scripts/deployment_time_capture.py \
  --label "k8s_onprem_deploy" \
  --service-url "${SERVICE_URL}" \
  --deploy-cmd "${DEPLOY_CMD}" \
  --output-file "analysis/deployment_time_results.csv"

