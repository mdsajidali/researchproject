#!/bin/bash
set -e

echo "[INFO] Starting Prometheus, Grafana, and exporters using Podman..."

# Create a network for monitoring containers
podman network create monitoring-net || true

# --- Prometheus ---
podman run -d --name prometheus \
  --net monitoring-net \
  -p 9091:9090 \
  -v $(pwd)/../monitoring/prometheus/prometheus.docker.yml:/etc/prometheus/prometheus.yml:ro \
  prom/prometheus:v2.55.0 \
  --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus

# --- Grafana ---
podman run -d --name grafana \
  --net monitoring-net \
  -p 3000:3000 \
  -v $(pwd)/../monitoring/grafana/datasource.yml:/etc/grafana/provisioning/datasources/datasource.yml:ro \
  -e GF_SECURITY_ADMIN_USER=admin \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana:11.1.4

# --- Node Exporter ---
podman run -d --name node-exporter \
  --net host \
  --pid host \
  -v /:/host:ro,rslave \
  quay.io/prometheus/node-exporter:v1.8.2 \
  --path.rootfs=/host

# --- cAdvisor ---
podman run -d --name cadvisor \
  --net host \
  --privileged \
  -p 8080:8080 \
  -v /:/rootfs:ro \
  -v /var/run:/var/run:ro \
  -v /sys:/sys:ro \
  -v /var/lib/containers:/var/lib/containers:ro \
  gcr.io/cadvisor/cadvisor:v0.49.1

# --- Blackbox Exporter ---
podman run -d --name blackbox-exporter \
  --net monitoring-net \
  -p 9115:9115 \
  -v $(pwd)/../monitoring/exporters/blackbox/blackbox.yml:/etc/blackbox_exporter/config.yml:ro \
  prom/blackbox-exporter:v0.25.0 \
  --config.file=/etc/blackbox_exporter/config.yml

echo "[SUCCESS] Monitoring stack running!"
echo "Prometheus: http://localhost:9091"
echo "Grafana:    http://localhost:3000"

