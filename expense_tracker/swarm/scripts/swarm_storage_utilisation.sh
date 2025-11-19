#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

# Grab container IDs
WEB_CID=$(docker ps --filter "name=expense_tracker_web" --format "{{.ID}}" | head -n1)
DB_CID=$(docker ps --filter "name=expense_tracker_db" --format "{{.ID}}" | head -n1)

CMD_WEB_FS="docker exec ${WEB_CID} sh -c \"df -m /app | tail -1 | awk '{print \$3}'\""
CMD_DB_FS="docker exec ${DB_CID} sh -c \"df -m /var/lib/postgresql/data | tail -1 | awk '{print \$3}'\""

python3 scripts/storage_utilisation_capture.py \
  --label "swarm_onprem_storage" \
  --commands "$CMD_WEB_FS" "$CMD_DB_FS" \
  --output-file "analysis/storage_utilisation_results.csv"

