#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Compute TCO (Total Cost of Ownership) for the Expense Tracker deployment."
    )

    parser.add_argument("--env", required=True, help="Environment label (e.g. k8s_onprem)")
    parser.add_argument("--cpu-cores", type=float, required=True, help="Total vCPU allocated")
    parser.add_argument("--ram-gb", type=float, required=True, help="Total RAM (GB) allocated")
    parser.add_argument("--storage-gb", type=float, required=True, help="Total storage used (GB)")

    parser.add_argument("--price-cpu", type=float, default=0.023, help="€/vCPU-hour")
    parser.add_argument("--price-ram", type=float, default=0.0032, help="€/GB-hour")
    parser.add_argument("--price-storage", type=float, default=0.10, help="€/GB-month")

    parser.add_argument(
        "--output-file",
        default="analysis/tco_results.csv",
        help="CSV file to append results"
    )

    args = parser.parse_args()

    timestamp = dt.datetime.utcnow().isoformat()

    # Compute hourly cost
    hourly_cpu_cost = args.cpu_cores * args.price_cpu
    hourly_ram_cost = args.ram_gb * args.price_ram

    # Storage billed monthly; convert to hourly
    hourly_storage_cost = (args.storage_gb * args.price_storage) / (30 * 24)

    hourly_total = hourly_cpu_cost + hourly_ram_cost + hourly_storage_cost
    monthly_total = hourly_total * 24 * 30

    out_path = Path(args.output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not out_path.exists()

    header = [
        "timestamp_utc", "env",
        "cpu_cores", "ram_gb", "storage_gb",
        "price_cpu", "price_ram", "price_storage",
        "hourly_total_eur", "monthly_total_eur"
    ]

    with out_path.open("a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)

        writer.writerow([
            timestamp,
            args.env,
            args.cpu_cores,
            args.ram_gb,
            args.storage_gb,
            args.price_cpu,
            args.price_ram,
            args.price_storage,
            round(hourly_total, 4),
            round(monthly_total, 2)
        ])


if __name__ == "__main__":
    main()

