#!/bin/bash
# ------------------------------------------------------------------
# Universal JMeter Load Test Runner (Cross-Orchestrator)
# Author: Sajid Ali
# ------------------------------------------------------------------
# Usage:
#   ./run_jmeter.sh [threads] [duration] [scenario_name]
# Example:
#   ./run_jmeter.sh 50 120 baseline
#   ./run_jmeter.sh 100 180 spike
# ------------------------------------------------------------------

set -e

# ------------------ CONFIG ------------------
TEST_PLAN="expense_crud_test.jmx"
RESULTS_DIR="./results"
REPORT_DIR="./report"

THREADS=${1:-50}
DURATION=${2:-120}
SCENARIO=${3:-baseline}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Detect orchestrator automatically or allow override
ORCHESTRATOR=${ORCHESTRATOR:-"k8s"}
ORCHESTRATOR_LOWER=$(echo "$ORCHESTRATOR" | tr '[:upper:]' '[:lower:]')

mkdir -p "$RESULTS_DIR" "$REPORT_DIR"

RESULTS_FILE="${RESULTS_DIR}/results_${ORCHESTRATOR_LOWER}_${SCENARIO}_${TIMESTAMP}.jtl"
REPORT_PATH="${REPORT_DIR}/report_${ORCHESTRATOR_LOWER}_${SCENARIO}_${TIMESTAMP}"

# ------------------ INFO ------------------
echo "------------------------------------------------------------"
echo "[INFO] Running JMeter Test Plan"
echo "------------------------------------------------------------"
echo " Plan:        $TEST_PLAN"
echo " Orchestrator: ${ORCHESTRATOR_LOWER}"
echo " Threads:     $THREADS"
echo " Duration:    ${DURATION}s"
echo " Scenario:    $SCENARIO"
echo " Results:     $RESULTS_FILE"
echo " Report:      $REPORT_PATH"
echo "------------------------------------------------------------"

# ------------------ RUN JMETER ------------------
jmeter -n -t "$TEST_PLAN" \
  -l "$RESULTS_FILE" \
  -e -o "$REPORT_PATH" \
  -Jthreads="$THREADS" \
  -Jduration="$DURATION"

# ------------------ DONE ------------------
echo ""
echo "[INFO] ✅ Test completed successfully."
echo "       Results: $RESULTS_FILE"
echo "       Report:  $REPORT_PATH"

