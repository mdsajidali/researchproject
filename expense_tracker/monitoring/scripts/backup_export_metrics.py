#!/usr/bin/env python3
"""
Cross-Orchestrator Prometheus Metric Exporter
Author: Sajid Ali
Purpose: Collect standardized metrics (CPU, Memory, HTTP Uptime)
         from Prometheus for Kubernetes, Docker Swarm, Nomad,
         Mesos, and OpenShift environments.
"""

import requests, csv, time, datetime, os

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
PROM_URL = os.getenv("PROM_URL", "http://127.0.0.1:9090/api/v1/query")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./data")
ORCHESTRATOR = os.getenv("ORCHESTRATOR", "k8s").lower()
SCENARIO = os.getenv("SCENARIO", "baseline").lower()
INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "60"))  # seconds

# Create filename automatically if not provided
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
DEFAULT_FILE = f"{OUTPUT_DIR}/metrics_{ORCHESTRATOR}_{SCENARIO}_{timestamp}.csv"
OUTPUT_FILE = os.getenv("OUTPUT_FILE", DEFAULT_FILE)

# -------------------------------------------------------------------
# METRIC DEFINITIONS
# -------------------------------------------------------------------
METRICS = {
    "cpu_usage": 'avg(rate(node_cpu_seconds_total{mode!="idle"}[1m]))',
    "memory_usage": 'node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes',
    "http_uptime": 'avg_over_time(probe_success[1m])'
}

# -------------------------------------------------------------------
# FUNCTIONS
# -------------------------------------------------------------------
def query(metric_name, promql):
    """Run a single Prometheus query and return value."""
    try:
        response = requests.get(PROM_URL, params={"query": promql}, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", {}).get("result", [])
        if data:
            return float(data[0]["value"][1])
        else:
            return 0.0
    except Exception as e:
        print(f"[WARN] Query failed for {metric_name}: {e}")
        return 0.0


def export_loop():
    """Continuously scrape metrics and append to CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"[INFO] Starting metric collection from {PROM_URL}")
    print(f"[INFO] Writing data to {OUTPUT_FILE} every {INTERVAL}s\n")

    # Write header if new file
    if not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) == 0:
        with open(OUTPUT_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp"] + list(METRICS.keys()))

    # Loop forever (Ctrl+C to stop)
    while True:
        timestamp = datetime.datetime.now().isoformat()
        row = [timestamp] + [query(k, v) for k, v in METRICS.items()]

        with open(OUTPUT_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        print(
            f"[INFO] {timestamp} | "
            + " | ".join([f"{k}:{v:.4f}" for k, v in zip(METRICS.keys(), row[1:])])
        )

        time.sleep(INTERVAL)


if __name__ == "__main__":
    export_loop()

