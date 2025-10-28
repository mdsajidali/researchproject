#!/bin/bash
# ------------------------------------------------------------------
# Run JMeter load test in non-GUI mode
# Author: Sajid Ali
# ------------------------------------------------------------------
# Usage:
#   ./run_jmeter.sh [threads] [duration] [scenario_name]
# Example:
#   ./run_jmeter.sh 50 120 baseline
#   ./run_jmeter.sh 100 120 spike
# ------------------------------------------------------------------

set -e

TEST_PLAN="expense_crud_test.jmx"
RESULTS_DIR="./results"
REPORT_DIR="./report"

THREADS=${1:-50}
DURATION=${2:-120}
SCENARIO=${3:-baseline}  # default scenario name if not provided
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$RESULTS_DIR" "$REPORT_DIR"

RESULTS_FILE="${RESULTS_DIR}/results_k8s_${SCENARIO}_${TIMESTAMP}.jtl"
REPORT_PATH="${REPORT_DIR}/report_k8s_${SCENARIO}_${TIMESTAMP}"

echo "[INFO] Running JMeter test plan: $TEST_PLAN"
echo "[INFO] Threads: $THREADS | Duration: ${DURATION}s | Scenario: $SCENARIO"
echo "[INFO] Results -> $RESULTS_FILE"
echo "[INFO] Report  -> $REPORT_PATH"

jmeter -n -t "$TEST_PLAN" \
  -l "$RESULTS_FILE" \
  -e -o "$REPORT_PATH" \
  -Jthreads="$THREADS" \
  -Jduration="$DURATION"

echo "[INFO] Test completed. Results saved at:"
echo "       $RESULTS_FILE"
echo "       $REPORT_PATH"

