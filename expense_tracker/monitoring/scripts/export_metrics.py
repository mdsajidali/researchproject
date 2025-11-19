#!/usr/bin/env python3
"""
Cross-Orchestrator Prometheus Metric Exporter (Final Thesis Version)
Author: Sajid Ali

Collects CPU (%), Memory (MB), HTTP uptime (%) from Prometheus.

For MicroShift/K8s we use node-level metrics (node_exporter)
+ blackbox probe_success for HTTP uptime.
"""

import requests, csv, time, datetime, os, sys

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
PROM_URL = os.getenv("PROM_URL", "http://127.0.0.1:9090/api/v1/query")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./data")
ORCHESTRATOR = os.getenv("ORCHESTRATOR", "k8s").lower()
SCENARIO = os.getenv("SCENARIO", "baseline").lower()
INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "10"))  # seconds

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
DEFAULT_FILE = f"{OUTPUT_DIR}/metrics_{ORCHESTRATOR}_{SCENARIO}_{timestamp}.csv"
OUTPUT_FILE = os.getenv("OUTPUT_FILE", DEFAULT_FILE)


# -------------------------------------------------------------------
# PROMQL QUERIES
# -------------------------------------------------------------------
def get_queries(orc: str):
    """
    Return orchestrator-specific PromQL queries.
    For MicroShift/K8s we intentionally use node-level metrics
    to avoid container label differences.
    """

    # MicroShift / K8s / OpenShift -> NODE METRICS + HTTP uptime
    if orc in ["k8s", "kubernetes", "openshift", "microshift"]:
        return {
            # CPU usage as % (non-idle)
            "cpu_usage": (
                'avg(rate(node_cpu_seconds_total{mode!="idle"}[1m])) * 100'
            ),
            # Memory usage in MB
            "memory_usage": (
                '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)'
                ' / 1024 / 1024'
            ),
            # HTTP uptime (%) from blackbox (any probe_success)
            "http_uptime": 'avg_over_time(probe_success[1m]) * 100',
        }

    # Swarm: keep as previously
    elif orc in ["swarm", "docker", "docker-swarm"]:
        return {
            "cpu_usage": (
                'sum(rate(container_cpu_usage_seconds_total{'
                'container_label_com_docker_swarm_service_name=~"expense_app|expense_db"'
                '}[1m]))'
            ),
            "memory_usage": (
                'sum(container_memory_usage_bytes{'
                'container_label_com_docker_swarm_service_name=~"expense_app|expense_db"'
                '}) / 1024 / 1024'
            ),
            "http_uptime": 'avg_over_time(probe_success[1m]) * 100',
        }

    # Nomad
    elif orc == "nomad":
        return {
            "cpu_usage": 'avg(nomad_client_allocs_cpu_total_percent)',
            "memory_usage": (
                'avg(nomad_client_allocs_memory_rss_bytes) / 1024 / 1024'
            ),
            "http_uptime": 'avg_over_time(probe_success[1m]) * 100',
        }

    # Fallback: node-level metrics
    else:
        return {
            "cpu_usage": (
                'avg(rate(node_cpu_seconds_total{mode!="idle"}[1m])) * 100'
            ),
            "memory_usage": (
                '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)'
                ' / 1024 / 1024'
            ),
            "http_uptime": 'avg_over_time(probe_success[1m]) * 100',
        }


METRICS = get_queries(ORCHESTRATOR)


# -------------------------------------------------------------------
# QUERY + EXPORT LOOP
# -------------------------------------------------------------------
def query(metric_name, promql):
    try:
        resp = requests.get(PROM_URL, params={"query": promql}, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", {}).get("result", [])
        if data:
            values = [float(v["value"][1]) for v in data if "value" in v]
            if not values:
                return 0.0
            return sum(values) / len(values)
        return 0.0
    except Exception as e:
        print(f"[WARN] {metric_name} failed: {e}")
        return 0.0


def export_loop():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n[INFO] Orchestrator: {ORCHESTRATOR}")
    print(f"[INFO] Prometheus: {PROM_URL}")
    print(f"[INFO] Scenario: {SCENARIO}")
    print(f"[INFO] Writing to: {OUTPUT_FILE} every {INTERVAL}s\n")

    # header
    with open(OUTPUT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp"] + list(METRICS.keys()))

    while True:
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        row_values = [query(k, v) for k, v in METRICS.items()]
        row = [ts] + row_values

        with open(OUTPUT_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        pretty = " | ".join(
            f"{k}:{v:.3f}"
            for k, v in zip(METRICS.keys(), row_values)
        )
        print(f"[{ts}] {pretty}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        export_loop()
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")
        sys.exit(0)

