#!/usr/bin/env python3
"""
Cross-Orchestrator Prometheus Metric Exporter (Final Unified Version)
Author: Sajid Ali
Updated by: ChatGPT
Purpose:
  Collect comparable metrics (CPU %, Memory %, HTTP uptime)
  across Kubernetes, Docker Swarm, MicroShift, and Nomad orchestrators.
  Automatically adapts between container- and node-level metrics.
"""

import requests, csv, time, datetime, os, sys

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
PROM_URL = os.getenv("PROM_URL", "http://localhost:9090")  # no /api/v1/query
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./data")
ORCHESTRATOR = os.getenv("ORCHESTRATOR", "nomad").lower()
SCENARIO = os.getenv("SCENARIO", "baseline").lower()
INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "10"))  # seconds

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
DEFAULT_FILE = f"{OUTPUT_DIR}/metrics_{ORCHESTRATOR}_{SCENARIO}_{timestamp}.csv"
OUTPUT_FILE = os.getenv("OUTPUT_FILE", DEFAULT_FILE)


# -------------------------------------------------------------------
# DYNAMIC QUERY SELECTION
# -------------------------------------------------------------------
def get_queries(orc: str):
    """
    Return orchestrator-specific PromQL queries.
    For Nomad, uses container-level (cAdvisor) metrics if present;
    otherwise, falls back to node-level metrics.
    """

    # --- Preferred: container-level metrics (used in earlier runs)
    container_queries = {
        "cpu_usage": 'sum(rate(container_cpu_usage_seconds_total{image!=""}[1m])) * 100',
        "memory_usage": 'sum(container_memory_usage_bytes{image!=""}) / 1024 / 1024',
        "http_uptime": 'avg_over_time(probe_success[1m])'
        #"cpu_usage": "sum(rate(container_cpu_usage_seconds_total[1m])) * 100",
        #"memory_usage": "100 * (sum(container_memory_usage_bytes) / sum(machine_memory_bytes))",
        #"http_uptime": "avg_over_time(probe_success[1m])"
    }

    # --- Fallback: node-level metrics
    node_queries = {
        "cpu_usage": "100 - (avg by (instance)(rate(node_cpu_seconds_total{mode='idle'}[1m])) * 100)",
        "memory_usage": "100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))",
        "http_uptime": "avg_over_time(probe_success[1m])"
    }

    # --- For Docker Swarm
    if orc in ["swarm", "docker", "docker-swarm"]:
        return {
            "cpu_usage": 'sum(rate(container_cpu_usage_seconds_total{container_label_com_docker_swarm_service_name="expense_app"}[1m])) * 100',
            "memory_usage": '100 * (sum(container_memory_usage_bytes{container_label_com_docker_swarm_service_name="expense_app"}) / sum(machine_memory_bytes))',
            "http_uptime": 'avg_over_time(probe_success[1m])'
        }

    # --- For K8s / MicroShift / Nomad: detect cAdvisor presence
    try:
        url = f"{PROM_URL}/api/v1/label/__name__/values"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        all_metrics = resp.json().get("data", [])
        if any(m.startswith("container_cpu_usage_seconds_total") for m in all_metrics):
            print("[INFO] Detected cAdvisor metrics — using container-level queries.")
            return container_queries
        else:
            print("[INFO] cAdvisor metrics not found — using node-level queries.")
            return node_queries
    except Exception:
        print("[WARN] Could not verify metrics list — defaulting to node-level queries.")
        return node_queries


METRICS = get_queries(ORCHESTRATOR)


# -------------------------------------------------------------------
# QUERY FUNCTION
# -------------------------------------------------------------------
def query(metric_name, promql):
    """Run a single Prometheus query and return numeric value."""
    try:
        url = f"{PROM_URL}/api/v1/query"
        response = requests.get(url, params={"query": promql}, timeout=10)
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", {}).get("result", [])
        if not data:
            return 0.0
        values = [float(item["value"][1]) for item in data if "value" in item]
        return sum(values) / len(values) if values else 0.0
    except Exception as e:
        print(f"[WARN] Query failed for {metric_name}: {e}")
        return 0.0


# -------------------------------------------------------------------
# MAIN EXPORT LOOP
# -------------------------------------------------------------------
def export_loop():
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
        results = [query(k, v) for k, v in METRICS.items()]
        row = [timestamp] + results

        with open(OUTPUT_FILE, "a", newline="") as f:
            csv.writer(f).writerow(row)

        pretty = " | ".join(f"{k}:{v:.4f}" for k, v in zip(METRICS.keys(), results))
        print(f"[{timestamp}] {pretty}")
        time.sleep(INTERVAL)


# -------------------------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------------------------
if __name__ == "__main__":
    try:
        export_loop()
    except KeyboardInterrupt:
        print("\n[INFO] Metric export stopped by user.")
        sys.exit(0)

