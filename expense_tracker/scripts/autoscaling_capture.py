#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import subprocess
import time
import re
from pathlib import Path


def get_replicas(cmd: str):
    """
    Run the replica-count command and try to extract an integer value.

    Returns:
        int or None
    """
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None

    if proc.returncode != 0:
        return None

    out = proc.stdout.strip().strip("'\"")
    if not out:
        return None

    m = re.search(r"\d+", out)
    if not m:
        return None

    try:
        return int(m.group())
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Capture auto-scaling behaviour (time to scale) for the Expense Tracker service.",
    )
    parser.add_argument(
        "--service-url",
        default="http://localhost:8000/",
        help="URL of the service (for reference only).",
    )
    parser.add_argument(
        "--replica-cmd",
        required=True,
        help="Shell command that prints the current number of replicas/pods/tasks.",
    )
    parser.add_argument(
        "--load-cmd",
        default="",
        help="Optional shell command to generate load (e.g. JMeter). If empty, no load is started.",
    )
    parser.add_argument(
        "--label",
        required=True,
        help="Label for this run (e.g. k8s_onprem_spike).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Max seconds to observe for scaling (default: 600).",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds between replica checks (default: 5.0).",
    )
    parser.add_argument(
        "--output-file",
        default="analysis/autoscaling_results.csv",
        help="CSV file to append results to (default: analysis/autoscaling_results.csv)",
    )

    args = parser.parse_args()

    out_path = Path(args.output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = dt.datetime.utcnow().isoformat()

    baseline_replicas = get_replicas(args.replica_cmd)
    status = "ok"
    time_to_first_scale = None
    max_replicas = baseline_replicas if baseline_replicas is not None else None

    if baseline_replicas is None:
        status = "baseline_replica_error"
    else:
        # Start load generator if provided
        load_start = time.time()
        load_proc = None
        if args.load_cmd.strip():
            try:
                load_proc = subprocess.Popen(args.load_cmd, shell=True)
            except Exception:
                status = "load_cmd_error"

        if status == "ok":
            deadline = load_start + args.timeout
            while time.time() < deadline:
                replicas = get_replicas(args.replica_cmd)
                if replicas is not None:
                    if max_replicas is None or replicas > max_replicas:
                        max_replicas = replicas
                    if (
                        time_to_first_scale is None
                        and replicas > baseline_replicas
                    ):
                        time_to_first_scale = time.time() - load_start
                        break
                time.sleep(args.interval)

            if time_to_first_scale is None and status == "ok":
                status = "no_scale"

        # Optional: we do not forcibly kill load_proc; JMeter stops by itself.

    header = [
        "timestamp_utc",
        "label",
        "service_url",
        "replica_cmd",
        "load_cmd",
        "baseline_replicas",
        "max_replicas",
        "time_to_first_scale_seconds",
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
                args.replica_cmd,
                args.load_cmd,
                baseline_replicas if baseline_replicas is not None else "",
                max_replicas if max_replicas is not None else "",
                f"{time_to_first_scale:.3f}"
                if time_to_first_scale is not None
                else "",
                status,
            ]
        )


if __name__ == "__main__":
    main()

