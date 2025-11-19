#!/usr/bin/env python3
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import f_oneway


# --------- CONFIG: adjust only if your layout differs ---------
ROOT = Path(__file__).resolve().parents[1]  # expense_tracker root
ANALYSIS_DIR = ROOT / "analysis"

PROMETHEUS_DIRS = [
    ROOT / "monitoring" / "scripts" / "data",
    ROOT / "data",
]

JMETER_RESULTS_DIR = ROOT / "jmeter" / "results"

# Orchestrator / env / scenario tokens we try to infer from filenames / labels
ORCH_TOKENS = ["swarm", "k8s", "nomad", "microshift"]
ENV_TOKENS = ["onprem", "cloud", "hybrid"]
SCENARIO_TOKENS = ["baseline", "spike", "fault", "autoscale"]


# --------- helpers ---------
def infer_labels_from_name(name: str):
    """
    Infer orchestrator, environment, scenario, run_id from a filename or label.
    Very tolerant: looks for known tokens and uses the rest as run_id.
    """
    base = Path(name).stem.lower()
    parts = re.split(r"[._\-]+", base)

    orch = next((p for p in parts if p in ORCH_TOKENS), "unknown")
    env = next((p for p in parts if p in ENV_TOKENS), "unknown")
    scen = next((p for p in parts if p in SCENARIO_TOKENS), "unknown")

    # run_id = everything that is not a known token, joined
    leftover = [p for p in parts if p not in ORCH_TOKENS + ENV_TOKENS + SCENARIO_TOKENS]
    run_id = "_".join(leftover) if leftover else base
    return orch, env, scen, run_id


# --------- 1) PROMETHEUS EXPORT CSVs (from export_metrics.py) ---------
def collect_prometheus_metrics():
    rows = []
    for d in PROMETHEUS_DIRS:
        if not d.exists():
            continue
        for path in d.glob("metrics_*.csv"):
            try:
                df = pd.read_csv(path)
            except Exception:
                continue

            orch, env, scen, run_id = infer_labels_from_name(path.name)

            cols = df.columns.str.lower()
            df.columns = cols

            # try to identify cpu, mem, uptime columns
            cpu_col = next((c for c in cols if "cpu" in c), None)
            mem_col = next((c for c in cols if "mem" in c or "memory" in c), None)
            up_col = next((c for c in cols if "http" in c and "uptime" in c), None)

            avg_cpu = df[cpu_col].mean() if cpu_col in df.columns else np.nan
            avg_mem = df[mem_col].mean() if mem_col in df.columns else np.nan
            uptime_pct = df[up_col].mean() * 100.0 if up_col in df.columns else np.nan

            rows.append(
                {
                    "orchestrator": orch,
                    "environment": env,
                    "scenario": scen,
                    "run_id": run_id,
                    "avg_cpu": float(avg_cpu) if not np.isnan(avg_cpu) else np.nan,
                    "avg_mem": float(avg_mem) if not np.isnan(avg_mem) else np.nan,
                    "uptime_pct": float(uptime_pct) if not np.isnan(uptime_pct) else np.nan,
                }
            )

    return pd.DataFrame(rows) if rows else pd.DataFrame()


# --------- 2) JMETER .JTL RESULTS ---------
def collect_jmeter_metrics():
    rows = []
    if not JMETER_RESULTS_DIR.exists():
        return pd.DataFrame()

    for path in JMETER_RESULTS_DIR.glob("*.jtl"):
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except Exception:
            continue

        times = []
        timestamps = []

        for sample in root.iter("httpSample"):
            t = sample.attrib.get("t")
            ts = sample.attrib.get("ts")
            if t is None:
                continue
            try:
                t_val = float(t)
                times.append(t_val)
                if ts is not None:
                    timestamps.append(float(ts))
            except ValueError:
                continue

        if not times:
            continue

        orch, env, scen, run_id = infer_labels_from_name(path.name)

        avg_latency = float(np.mean(times))

        if timestamps:
            duration_s = (max(timestamps) - min(timestamps)) / 1000.0
            duration_s = duration_s if duration_s > 0 else 1.0
        else:
            duration_s = len(times)  # crude default

        throughput_rps = len(times) / duration_s

        rows.append(
            {
                "orchestrator": orch,
                "environment": env,
                "scenario": scen,
                "run_id": run_id,
                "avg_latency_ms": avg_latency,
                "throughput_rps": throughput_rps,
            }
        )

    return pd.DataFrame(rows) if rows else pd.DataFrame()


# --------- 3) OPTIONAL ADDITIONAL METRICS FROM EARLIER SCRIPTS ---------
def load_optional_metric_csv(filename, value_col, new_colname):
    """
    Generic loader for optional CSVs created by earlier steps.
    Expects a 'label' column that contains env/orchestrator/scenario info.
    """
    path = ANALYSIS_DIR / filename
    if not path.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

    if "label" not in df.columns or value_col not in df.columns:
        return pd.DataFrame()

    rows = []
    for _, row in df.iterrows():
        label = str(row["label"])
        val = row[value_col]
        if pd.isna(val):
            continue
        orch, env, scen, run_id = infer_labels_from_name(label)
        rows.append(
            {
                "orchestrator": orch,
                "environment": env,
                "scenario": scen,
                "run_id": run_id,
                new_colname: float(val),
            }
        )

    return pd.DataFrame(rows)


def load_deploy_time():
    path = ANALYSIS_DIR / "deployment_time_results.csv"
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

    if "deploy_cmd" not in df.columns or "deployment_seconds" not in df.columns:
        return pd.DataFrame()

    rows = []
    for _, row in df.iterrows():
        label = str(row.get("label", row.get("deploy_cmd", "")))
        orch, env, scen, run_id = infer_labels_from_name(label)
        val = row.get("deployment_seconds")
        if pd.isna(val):
            continue
        rows.append(
            {
                "orchestrator": orch,
                "environment": env,
                "scenario": scen,
                "run_id": run_id,
                "deploy_seconds": float(val),
            }
        )
    return pd.DataFrame(rows)


def load_tco():
    path = ANALYSIS_DIR / "tco_results.csv"
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

    if "env" not in df.columns or "monthly_total_eur" not in df.columns:
        return pd.DataFrame()

    rows = []
    for _, row in df.iterrows():
        label = str(row["env"])
        orch, env, scen, run_id = infer_labels_from_name(label)
        val = row["monthly_total_eur"]
        if pd.isna(val):
            continue
        rows.append(
            {
                "orchestrator": orch,
                "environment": env,
                "scenario": scen,
                "run_id": run_id,
                "tco_monthly_eur": float(val),
            }
        )
    return pd.DataFrame(rows)


def load_complexity():
    path = ANALYSIS_DIR / "complexity_results.csv"
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

    if "env" not in df.columns or "complexity_score" not in df.columns:
        return pd.DataFrame()

    rows = []
    for _, row in df.iterrows():
        label = str(row["env"])
        orch, env, scen, run_id = infer_labels_from_name(label)
        val = row["complexity_score"]
        if pd.isna(val):
            continue
        rows.append(
            {
                "orchestrator": orch,
                "environment": env,
                "scenario": scen,
                "run_id": run_id,
                "complexity_score": float(val),
            }
        )
    return pd.DataFrame(rows)


# --------- 4) BUILD MASTER DATAFRAME ---------
def build_master_df():
    # Core: Prometheus + JMeter (always used)
    prom = collect_prometheus_metrics()
    jmt = collect_jmeter_metrics()

    if prom.empty and jmt.empty:
        raise SystemExit("No Prometheus or JMeter metrics found. Nothing to analyse.")

    # Merge core metrics
    if prom.empty:
        core = jmt
    elif jmt.empty:
        core = prom
    else:
        core = pd.merge(
            prom,
            jmt,
            on=["orchestrator", "environment", "scenario", "run_id"],
            how="outer",
        )

    # Optional extras (if you did not run those scripts, these just skip)
    fr = load_optional_metric_csv(
        "failure_recovery_results.csv", "recovery_seconds", "recovery_seconds"
    )
    autos = load_optional_metric_csv(
        "autoscaling_results.csv", "time_to_first_scale_seconds", "time_to_first_scale"
    )
    deploy = load_deploy_time()
    tco = load_tco()
    cx = load_complexity()
    storage = load_optional_metric_csv(
        "storage_utilisation_results.csv", "total_mb", "storage_total_mb"
    )

    for extra in [fr, autos, deploy, tco, cx, storage]:
        if not extra.empty:
            core = pd.merge(
                core,
                extra,
                on=["orchestrator", "environment", "scenario", "run_id"],
                how="left",
            )

    # Save master CSV
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    master_path = ANALYSIS_DIR / "metrics_master.csv"
    core.to_csv(master_path, index=False)
    print(f"[OK] Master metrics saved to {master_path}")
    return core


# --------- 5) RUN ONE-WAY ANOVA PER METRIC / ENVIRONMENT ---------
def run_anova(core: pd.DataFrame):
    numeric_cols = core.select_dtypes(include=[np.number]).columns.tolist()
    # Remove run_id if numeric
    numeric_cols = [c for c in numeric_cols if c not in ["run_id"]]

    envs = core["environment"].fillna("unknown").unique()

    lines = []
    lines.append("ANOVA RESULTS (one-way, factor = orchestrator, per environment)\n")
    lines.append("================================================================\n\n")

    for metric in numeric_cols:
        lines.append(f"Metric: {metric}\n")
        for env in envs:
            sub = core[core["environment"].fillna("unknown") == env]
            if sub["orchestrator"].nunique() < 2:
                continue

            groups = []
            labels = []
            for orch in sorted(sub["orchestrator"].dropna().unique()):
                vals = sub.loc[sub["orchestrator"] == orch, metric].dropna().values
                if len(vals) > 1:
                    groups.append(vals)
                    labels.append(orch)

            if len(groups) < 2:
                continue

            try:
                F, p = f_oneway(*groups)
            except Exception:
                continue

            sig = "SIGNIFICANT" if p < 0.05 else "not significant"
            lines.append(f"  Environment: {env}\n")
            lines.append(f"    Groups: {', '.join(labels)}\n")
            lines.append(f"    F = {F:.4f}, p = {p:.6f} ({sig})\n")
        lines.append("\n")

    out_path = ANALYSIS_DIR / "anova_results.txt"
    with out_path.open("w") as f:
        f.writelines(lines)

    print(f"[OK] ANOVA results written to {out_path}")


def main():
    core = build_master_df()
    run_anova(core)


if __name__ == "__main__":
    main()

