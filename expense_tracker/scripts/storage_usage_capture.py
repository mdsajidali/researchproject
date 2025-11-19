#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import subprocess
from pathlib import Path
import re


def run_cmd(cmd: str):
    """ Run a shell command and return its stdout (string). """
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return out.decode().strip()
    except Exception:
        return ""


def extract_mb(text: str):
    """
    Extract a numeric value representing MB from df-like command output.
    Returns None if no number found.
    """
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if not m:
        return None
    return float(m.group(1))


def main():
    parser = argparse.ArgumentParser(
        description="Capture storage utilisation for any orchestrator environment."
    )
    parser.add_argument(
        "--label", required=True, help="Run label (e.g., k8s_onprem_storage)"
    )
    parser.add_argument(
        "--node-cmd",
        required=True,
        help="Command returning node filesystem usage in MB (e.g., df -m / | tail -1 | awk '{print $3}')",
    )
    parser.add_argument(
        "--container-cmd",
        default="",
        help="Optional: command returning container/pod storage usage in MB.",
    )
    parser.add_argument(
        "--pv-cmd",
        default="",
        help="Optional: command returning PV/PVC usage in MB.",
    )
    parser.add_argument(
        "--output-file",
        default="analysis/storage_usage_results.csv",
        help="CSV output (default: analysis/storage_usage_results.csv)",
    )

    args = parser.parse_args()

    out_path = Path(args.output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = dt.datetime.utcnow().isoformat()

    node_raw = run_cmd(args.node_cmd)
    container_raw = run_cmd(args.container_cmd) if args.container_cmd else ""
    pv_raw = run_cmd(args.pv_cmd) if args.pv_cmd else ""

    node_mb = extract_mb(node_raw)
    container_mb = extract_mb(container_raw) if container_raw else None
    pv_mb = extract_mb(pv_raw) if pv_raw else None

    header = [
        "timestamp_utc",
        "label",
        "node_usage_mb",
        "container_usage_mb",
        "pv_usage_mb",
        "node_cmd",
        "container_cmd",
        "pv_cmd",
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
                f"{node_mb:.2f}" if node_mb else "",
                f"{container_mb:.2f}" if container_mb else "",
                f"{pv_mb:.2f}" if pv_mb else "",
                args.node_cmd,
                args.container_cmd,
                args.pv_cmd,
            ]
        )


if __name__ == "__main__":
    main()

