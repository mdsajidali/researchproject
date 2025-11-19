#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

# Requires Nomad & Docker integration
WEB_ALLOC=$(nomad alloc status -json $(nomad job allocs expense-tracker -json | jq -r '.[0].ID') | jq -r '.TaskStates.web.ContainerID')
DB_ALLOC=$(nomad alloc status -json $(nomad job allocs expense-tracker -json | jq -r '.[0].ID') | jq -r '.TaskStates.db.ContainerID')

CMD_WEB_FS="docker exec ${WEB_ALLOC} sh -c \"df -m /app | tail -1 | awk '{print \$3}'\""
CMD_DB_FS="docker exec ${DB_ALLOC} sh -c \"df -m /var/lib/postgresql/data | tail -1 | awk '{print \$3}'\""

python3 scripts/storage_utilisation_capture.py \
  --label 'nomad_onprem_storage' \
  --commands "$CMD_WEB_FS" "$CMD_DB_FS" \
  --output-file "analysis/storage_utilisation_results.csv"

