#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

CPU=2
RAM=4
STORAGE_GB=$(awk -F',' 'NR>1 {print $NF}' analysis/storage_utilisation_results.csv | tail -1)
STORAGE_GB=$(echo "$STORAGE_GB / 1024" | bc -l)

python3 scripts/tco_capture.py \
  --env microshift_cloud \
  --cpu-cores $CPU \
  --ram-gb $RAM \
  --storage-gb $STORAGE_GB

