#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
from pathlib import Path


def compute_score(deploy_s, config_lines, manual_steps, error_count, tool_weight):
    # Normalisations (tuned for your project scale)
    deploy_norm = min(deploy_s / 300, 1.0)          # 0–300s
    config_norm = min(config_lines / 800, 1.0)      # 0–800 lines
    manual_norm = min(manual_steps / 20, 1.0)       # 0–20
    error_norm = min(error_count / 10, 1.0)         # 0–10

    # Weighted sum
    base = (
        deploy_norm * 0.40 +
        config_norm * 0.30 +
        manual_norm * 0.20 +
        error_norm * 0.10
    )

    return round(base * tool_weight * 100, 2)


def main():
    parser = argparse.ArgumentParser(
        description="Compute implementation complexity score."
    )

    parser.add_argument("--env", required=True, help="Environment identifier")
    parser.add_argument("--deploy-seconds", type=float, required=True)
    parser.add_argument("--config-lines", type=int, required=True)
    parser.add_argument("--manual-steps", type=int, required=True)
    parser.add_argument("--error-count", type=int, default=0)

    # Default difficulty factors (based on your ranking)
    parser.add_argument(
        "--tool-weight", type=float, default=1.0,
        help="Weight: microshift=1.3, nomad=1.15, k8s=1.0, swarm=0.85"
    )

    parser.add_argument(
        "--output-file",
        default="analysis/complexity_results.csv"
    )

    args = parser.parse_args()
    timestamp = dt.datetime.utcnow().isoformat()

    score = compute_score(
        args.deploy_seconds,
        args.config_lines,
        args.manual_steps,
        args.error_count,
        args.tool_weight
    )

    out_path = Path(args.output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    write_header = not out_path.exists()

    header = [
        "timestamp_utc", "env",
        "deploy_seconds", "config_lines",
        "manual_steps", "error_count",
        "tool_weight", "complexity_score"
    ]

    with out_path.open("a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerow([
            timestamp,
            args.env,
            args.deploy_seconds,
            args.config_lines,
            args.manual_steps,
            args.error_count,
            args.tool_weight,
            score
        ])


if __name__ == "__main__":
    main()

