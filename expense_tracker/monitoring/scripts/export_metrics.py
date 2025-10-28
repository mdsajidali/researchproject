#!/usr/bin/env python3
"""
Cross-Orchestrator Prometheus Metric Exporter
Author: Sajid Ali
Purpose:
  Collect standardized metrics (CPU, Memory, HTTP uptime)
  from Prometheus for Kubernetes, Docker Swarm, Nomad, Mesos, and OpenShift.
"""

import requests, csv, time, datetime, os, sys

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
PROM_URL = os.getenv("PROM_URL", "http://127.0.0.1:9090/api/v1/query")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./data")
ORCHESTRATOR = os.getenv("ORCHESTRATOR", "k8s").lower()
SCENARIO = os.getenv("SCENARIO", "baseline").lower()
INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "60"))  # seconds

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
DEFAULT_FILE = f"{OUTPUT_DIR}/metrics_{ORCHESTRATOR}_{SCENARIO}_{timestamp}.csv"
OUTPUT_FILE = os.getenv("OUTPUT_FILE", DEFAULT_FILE)

# -------------------------------------------------------------------
# DYNAMIC METRIC DEFINITIONS
# -------------------------------------------------------------------
def get_queries(orc: str):
    """Return orchestrator-specific PromQL queries."""
    if orc in ["k8s", "kubernetes", "openshift"]:
        return {
            "cpu_usage": 'sum(rate(container_cpu_usage_seconds_total{container!="",pod!=""}[1m])) by (pod)',
            "memory_usage": 'sum(container_memory_usage_bytes{container!="",pod!=""}) by (pod)',
            "http_uptime": 'avg_over_time(probe_success[1m])'
        }

    elif orc in ["swarm", "docker", "docker-swarm"]:
        return {
            "cpu_usage": 'sum(rate(container_cpu_usage_seconds_total{container_label_com_docker_swarm_service_name="expense_app"}[1m]))',
            "memory_usage": 'avg(container_memory_usage_bytes{container_label_com_docker_swarm_service_name="expense_app"})',
            "http_uptime": 'avg_over_time(probe_success[1m])'
        }

    elif orc == "nomad":
        return {
            "cpu_usage": 'avg(nomad_client_allocs_cpu_total_percent)',
            "memory_usage": 'avg(nomad_client_allocs_memory_rss_bytes)',
            "http_uptime": 'avg_over_time(probe_success[1m])'
        }

    elif orc == "mesos":
        return {
            "cpu_usage": 'avg(mesos_task_cpu_usage_seconds_total)',
            "memory_usage": 'avg(mesos_task_memory_rss_bytes)',
            "http_uptime": 'avg_over_time(probe_success[1m])'
        }

    else:
        print(f"[WARN] Unknown orchestrator '{orc}', using generic node metrics.")
        return {
            "cpu_usage": 'avg(rate(node_cpu_seconds_total{mode!="idle"}[1m]))',
            "memory_usage": 'node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes',
            "http_uptime": 'avg_over_time(probe_success[1m])'
        }


METRICS = get_queries(ORCHESTRATOR)

# -------------------------------------------------------------------
# FUNCTIONS
# -------------------------------------------------------------------
def query(metric_name, promql):
    """Run a single Prometheus query and return numeric value."""
    try:
        response = requests.get(PROM_URL, params={"query": promql}, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", {}).get("result", [])
        if data:
            # sum multiple results if vector
            values = [float(v["value"][1]) for v in data if "value" in v]
            return sum(values) / len(values)
        return 0.0
    except Exception as e:
        print(f"[WARN] Query failed for {metric_name}: {e}")
        return 0.0


def export_loop():
    """Continuously scrape metrics and append to CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n[INFO] Orchestrator: {ORCHESTRATOR}")
    print(f"[INFO] Starting metric collection from {PROM_URL}")
    print(f"[INFO] Writing data to {OUTPUT_FILE} every {INTERVAL}s\n")

    if not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) == 0:
        with open(OUTPUT_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp"] + list(METRICS.keys()))

    while True:
        timestamp = datetime.datetime.now().isoformat(timespec="seconds")
        row = [timestamp] + [query(k, v) for k, v in METRICS.items()]

        with open(OUTPUT_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        pretty = " | ".join([f"{k}:{v:.4f}" for k, v in zip(METRICS.keys(), row[1:])])
        print(f"[{timestamp}] {pretty}")

        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        export_loop()
    except KeyboardInterrupt:
        print("\n[INFO] Metric export stopped by user.")
        sys.exit(0)

