#!/bin/bash
threads=$1
duration=$2
scenario=$3

timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="results/results_nomad_${scenario}_${timestamp}.jtl"
report_dir="report/report_nomad_${scenario}_${timestamp}"

mkdir -p report

jmeter -n \
  -t expense_crud_test.jmx \
  -Jtarget_host=192.168.74.128 \
  -Jtarget_port=8000 \
  -Jthreads=$threads \
  -Jduration=$duration \
  -l $results_dir \
  -e -o $report_dir

