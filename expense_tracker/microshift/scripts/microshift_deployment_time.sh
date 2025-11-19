#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SERVICE_URL="${SERVICE_URL:-http://localhost:8000/}"

# Default assumes your app manifests live under microshift/app/
DEPLOY_CMD="${DEPLOY_CMD:-oc apply -f microshift/app/}"

python3 scripts/deployment_time_capture.py \
  --label "microshift_cloud_deploy" \
  --service-url "${SERVICE_URL}" \
  --deploy-cmd "${DEPLOY_CMD}" \
  --output-file "analysis/deployment_time_results.csv"

