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
    Poll the given URL until it returns HTTP 200 or the timeout is reached.
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


def main():
    parser = argparse.ArgumentParser(
        description="Measure deployment time for the Expense Tracker service."
    )
    parser.add_argument(
        "--service-url",
        default="http://localhost:8000/",
        help="URL to check for readiness (default: http://localhost:8000/).",
    )
    parser.add_argument(
        "--deploy-cmd",
        required=True,
        help="Shell command that performs the deployment (kubectl apply, docker stack deploy, etc.).",
    )
    parser.add_argument(
        "--label",
        required=True,
        help="Label for this run (e.g. k8s_onprem_deploy, swarm_cloud_deploy).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="Max seconds to wait for the service to become healthy (default: 900).",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=3.0,
        help="Seconds between health checks (default: 3.0).",
    )
    parser.add_argument(
        "--output-file",
        default="analysis/deployment_time_results.csv",
        help="CSV file to append results to (default: analysis/deployment_time_results.csv).",
    )

    args = parser.parse_args()

    out_path = Path(args.output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = dt.datetime.utcnow().isoformat()
    deployment_seconds = None
    status = "ok"

    start = time.time()
    proc = subprocess.run(args.deploy_cmd, shell=True)
    if proc.returncode != 0:
        status = "deploy_cmd_error"
    else:
        healthy = wait_for_healthy(args.service_url, args.timeout, args.interval)
        if healthy:
            deployment_seconds = time.time() - start
        else:
            status = "timeout"

    header = [
        "timestamp_utc",
        "label",
        "service_url",
        "deploy_cmd",
        "deployment_seconds",
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
                args.deploy_cmd,
                f"{deployment_seconds:.3f}" if deployment_seconds is not None else "",
                status,
            ]
        )


if __name__ == "__main__":
    main()

