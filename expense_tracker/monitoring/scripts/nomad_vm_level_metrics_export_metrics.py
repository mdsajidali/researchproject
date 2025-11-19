#!/usr/bin/env python3
import requests, csv, time, datetime, os, sys

PROM_URL = os.getenv("PROM_URL", "http://54.146.16.229:9090")  # no /api/v1/query here
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./data")
ORCHESTRATOR = os.getenv("ORCHESTRATOR", "nomad").lower()
SCENARIO = os.getenv("SCENARIO", "baseline").lower()
INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "10"))  # seconds

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
DEFAULT_FILE = f"{OUTPUT_DIR}/metrics_{ORCHESTRATOR}_{SCENARIO}_{timestamp}.csv"
OUTPUT_FILE = os.getenv("OUTPUT_FILE", DEFAULT_FILE)

def get_queries(orc: str):
    """Return orchestrator-specific PromQL queries."""
    # For Nomad + Node Exporter + Blackbox setup
    if orc in ["nomad", "k8s", "microshift"]:
        return {
            # Average CPU usage % across all cores
            "cpu_usage": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode='idle'}[1m])) * 100)",

            # Memory usage % based on MemAvailable vs MemTotal
            "memory_usage": "100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))",

            # HTTP uptime (from blackbox exporter)
            "http_uptime": "avg_over_time(probe_success[1m])"
        }

    elif orc in ["swarm", "docker", "docker-swarm"]:
        return {
            "cpu_usage": 'sum(rate(container_cpu_usage_seconds_total[1m]))',
            "memory_usage": 'sum(container_memory_usage_bytes)',
            "http_uptime": 'avg_over_time(probe_success[1m])'
        }

    else:
        # Fallback: host-level node exporter metrics
        return {
            "cpu_usage": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode='idle'}[1m])) * 100)",
            "memory_usage": "100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))",
            "http_uptime": "avg_over_time(probe_success[1m])"
        }

METRICS = get_queries(ORCHESTRATOR)

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
        results = [query(k, v) for k, v in METRICS.items()]
        row = [timestamp] + results

        with open(OUTPUT_FILE, "a", newline="") as f:
            csv.writer(f).writerow(row)

        pretty = " | ".join(f"{k}:{v:.4f}" for k, v in zip(METRICS.keys(), results))
        print(f"[{timestamp}] {pretty}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        export_loop()
    except KeyboardInterrupt:
        print("\n[INFO] Metric export stopped by user.")
        sys.exit(0)

