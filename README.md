```markdown
# Expense Tracker – MSc Research Project

This repository contains the **Django Expense Tracker** application and all deployment artifacts for my MSc Cloud Computing thesis:

**“A Cross-Environment Evaluation Framework for Container Orchestration Tools: Optimizing Efficiency and Implementation Trade-offs for Real-World Workloads.”**

---

## Project Overview

The goal of this project is to benchmark multiple **container orchestration platforms** across on-premises, cloud, and hybrid environments, using a real-world workload (this Django application).

### Orchestrators evaluated:
- [x] Kubernetes (k3s, EKS)
- [x] Docker Swarm
- [x] HashiCorp Nomad

### Monitoring & Testing tools:
- Prometheus + Grafana
- ELK Stack (optional, stretch goal)
- Apache JMeter

### Metrics collected:
- **Quantitative:** latency, throughput, CPU/memory usage, fault recovery time, total cost of ownership (TCO).
- **Qualitative:** setup complexity, scalability, ease of use.

---

## Repository Structure

```

researchproject/
│
├── expense_tracker/      # Django app source code
├── docker/               # Dockerfiles and Compose configs
├── k8s/                  # Kubernetes manifests
├── swarm/                # Docker Swarm stack files
├── nomad/                # Nomad job specs
├── monitoring/           # Prometheus, Grafana, ELK configs
├── jmeter/               # JMeter load test plans and results
├── documentation/                 # Screenshots, weekly logs, environment notes
└── README.md             # Project overview and instructions

````

---

## Local Development (Docker Compose)

Build and run the application locally with PostgreSQL:

```bash
cd docker
docker compose up --build
````

Access the app at:
👉 [http://localhost:8000/](http://localhost:8000/)

---

## Deployments
### docker image tag:

docker tag expense_tracker-web:latest mdsajidali/expense-tracker:1.0

### 1. Kubernetes (k3s / EKS)

Apply manifests:

```bash
kubectl apply -f k8s/
kubectl -n expense get pods,svc
```

Expose service and access via NodePort or LoadBalancer.

---

### 2. Docker Swarm

Initialize Swarm:

```bash
docker swarm init
```

Deploy stack:

```bash
docker stack deploy -c swarm/stack.yml expenses
```

Check services:

```bash
docker stack services expenses
```

---

### 3. Nomad

Run Nomad agent in dev mode:

```bash
nomad agent -dev -bind 0.0.0.0
```

Deploy job:

```bash
nomad job run nomad/expense.nomad.hcl
```

---

## Monitoring & Load Testing

### Prometheus + Grafana

Start monitoring stack (local):

```bash
cd monitoring
docker compose up -d
```

* Prometheus → [http://localhost:9090](http://localhost:9090)
* Grafana → [http://localhost:3000](http://localhost:3000) (default admin/admin)

### JMeter

Run load test:

```bash
jmeter -n -t jmeter/expense_test_plan.jmx -l jmeter/results/output.jtl
```

---

##  Documentation

* **Weekly logs:** `docs/weekly_logs/`
* **Screenshots:** `docs/screenshots/`
* **Environment specs:** `docs/environment.md`

---
```
