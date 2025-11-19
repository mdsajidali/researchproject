#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import subprocess
import time
from pathlib import Path

import requests


def wait_for_healthy(url: str, timeout: int, interval: float) -> bool:
    """
    Wait until the service at `url` responds with HTTP 200 or timeout.

    Returns True if healthy, False if not.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(interval)
    return False


def measure_recovery(url: str, failure_cmd: str, timeout: int, interval: float):
    """
    Execute `failure_cmd` (shell) and then poll `url` until it is healthy again.

    Returns (recovery_seconds, status_string).
    """
    start = time.time()
    proc = subprocess.run(failure_cmd, shell=True)
    if proc.returncode != 0:
        # Failure injection itself failed; record and stop.
        return None, "failure_cmd_error"

    deadline = start + timeout

    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                end = time.time()
                return end - start, "ok"
        except Exception:
            pass
        time.sleep(interval)

    return None, "timeout"


def main():
    parser = argparse.ArgumentParser(
        description="Measure failure recovery time for the Expense Tracker service."
    )
    parser.add_argument(
        "--service-url",
        default="http://localhost:8000/",
        help="URL to probe for health (default: http://localhost:8000/)",
    )
    parser.add_argument(
        "--failure-cmd",
        required=True,
        help="Shell command that injects a failure (e.g. kubectl delete pod ...)",
    )
    parser.add_argument(
        "--label",
        required=True,
        help="Label for this run (e.g. k8s_onprem_baseline, swarm_cloud_fault).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Max seconds to wait for recovery (default: 300).",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Seconds between health checks (default: 2.0).",
    )
    parser.add_argument(
        "--output-file",
        default="analysis/failure_recovery_results.csv",
        help="CSV file to append results to (default: analysis/failure_recovery_results.csv)",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    out_path = Path(args.output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 1) Check baseline health
    baseline_ok = wait_for_healthy(args.service_url, timeout=60, interval=args.interval)

    timestamp = dt.datetime.utcnow().isoformat()
    recovery_seconds = None
    status = "baseline_unhealthy"

    if baseline_ok:
        # 2) Measure recovery after failure injection
        recovery_seconds, status = measure_recovery(
            args.service_url,
            args.failure_cmd,
            timeout=args.timeout,
            interval=args.interval,
        )

    # 3) Append result to CSV
    header = [
        "timestamp_utc",
        "label",
        "service_url",
        "failure_cmd",
        "recovery_seconds",
        "status",
    ]
    write_header = not out_path.exists()

    with out_path.open("a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow(
            [
                timestamp,
                args.label,
                args.service_url,
                args.failure_cmd,
                f"{recovery_seconds:.3f}" if recovery_seconds is not None else "",
                status,
            ]
        )


if __name__ == "__main__":
    main()

