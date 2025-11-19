#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

NS="edge-demo"
WEB_POD=$(oc -n $NS get pod -l app=expense-tracker -o jsonpath='{.items[0].metadata.name}')
DB_POD=$(oc -n $NS get pod -l app=db -o jsonpath='{.items[0].metadata.name}')

CMD_WEB_FS="oc -n ${NS} exec ${WEB_POD} -- df -m /app | tail -1 | awk '{print \$3}'"
CMD_DB_FS="oc -n ${NS} exec ${DB_POD} -- df -m /var/lib/postgresql/data | tail -1 | awk '{print \$3}'"

python3 scripts/storage_utilisation_capture.py \
  --label 'microshift_storage' \
  --commands "$CMD_WEB_FS" "$CMD_DB_FS" \
  --output-file "analysis/storage_utilisation_results.csv"

