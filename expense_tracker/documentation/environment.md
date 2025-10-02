# Environment Setup

This file documents the system environment, VM configuration, and software stack used for the MSc Cloud Computing thesis project:

**“A Cross-Environment Evaluation Framework for Container Orchestration Tools: Optimizing Efficiency and Implementation Trade-offs for Real-World Workloads.”**

---

## 1. Host System

- **Host Machine:** Windows 11 (64-bit)
- **Virtualization:** VMware Workstation
- **VM Image:** CentOS Stream 10

---

## 2. Virtual Machine Configuration

- **Memory:** 2 GB
- **vCPUs:** 2
- **Disk:** 40 GB (SCSI)
- **Network Adapter:** NAT
- **Other Devices:** USB Controller (enabled), Sound & Display auto-detect

*(Screenshot of VM settings stored in `docs/screenshots/week1/`)*

---

## 3. Operating System

- **OS:** CentOS Stream 10
- **Kernel Version:** `uname -r` → (record actual value)
- **Architecture:** x86_64

---

## 4. Installed Software

| Software         | Version (at install time) |
|------------------|----------------------------|
| Python           | 3.11.x                     |
| Django           | 4.2.x                      |
| PostgreSQL       | 15.x                       |
| Docker           | 26.x (Engine)              |
| Docker Compose   | v2.x                       |
| Git              | 2.x                        |
| cURL             | 8.x                        |

---

## 5. Container Orchestrators

- **k3s (Lightweight Kubernetes):**
  - Install method: `curl -sfL https://get.k3s.io | sh -`
  - Version: `k3s --version` → (record actual)

- **Docker Swarm:**
  - Installed as part of Docker Engine
  - Initialization: `docker swarm init`
  - Version: `docker --version` → (record actual)

- **Nomad:**
  - Install method: HashiCorp release binary
  - Version: `nomad version` → (record actual)
  - Run mode: `nomad agent -dev -bind 0.0.0.0`

---

## 6. Monitoring Tools (to be added later)

- Prometheus → planned version 2.54.x
- Grafana → planned version 11.x
- ELK Stack → optional stretch goal

---

## 7. Load Testing Tools

- Apache JMeter → 5.6.x

---

## 8. Notes

- Due to VM resource limits (2 GB RAM, 2 vCPUs), orchestrators are tested **one at a time** to ensure fairness and avoid memory starvation.
- Monitoring stack (Prometheus + Grafana) is run only during performance testing phases.

---
