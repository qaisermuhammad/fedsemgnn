#!/usr/bin/env python3
"""
Multi-scale scalability experiment runner for FedSemGNN.
Runs FedSemGNN at progressively larger node counts using generated topologies
with REAL EdgeSimPy simulation (actual EdgeServer/User/Service objects).

Usage:
    python experiments/run_scalability.py

Output:
    results/scalability/scalability_results.csv
"""
import os
import sys
import time
import json
import subprocess
import csv
from pathlib import Path

# Use venv python
PYTHON = os.path.join(os.path.dirname(__file__), '..', '.venv', 'Scripts', 'python.exe')
if not os.path.exists(PYTHON):
    PYTHON = sys.executable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Scalability sweep configuration
# (node_count, steps) — fewer steps at larger scales for feasibility
SCALE_CONFIGS = [
    (6,     50),    # native dataset (no generated topology)
    (25,    50),
    (50,    50),
    (100,   30),
    (200,   20),
    (500,   10),
    (1000,  5),
    (2000,  3),
    (5000,  2),
]

ALGORITHM = "FedSemGNN"
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "scalability")
METRICS_CSV = os.path.join(PROJECT_ROOT, "results", "fedsemgnn_metrics.csv")


def run_experiment(node_count, steps, use_generated_topology=True):
    """Run a single experiment at a given scale and return timing + metrics."""
    print(f"\n{'='*70}")
    print(f"  SCALE: {node_count} nodes, {steps} steps")
    print(f"{'='*70}")

    cmd = [
        PYTHON,
        os.path.join(PROJECT_ROOT, "main.py"),
        "--steps", str(steps),
        "--algorithm", ALGORITHM,
        "--override-num-nodes", str(node_count),
    ]
    if use_generated_topology and node_count > 6:
        cmd.extend([
            "--use-generated-topology",
            "--topology-mode", "random",
            "--topology-degree", "8",
        ])

    print(f"  CMD: {' '.join(cmd)}")

    # Delete old metrics file to ensure fresh data
    if os.path.exists(METRICS_CSV):
        os.remove(METRICS_CSV)

    t0 = time.time()
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=3600,  # 1 hour max per experiment
    )
    wall_time = time.time() - t0

    if result.returncode != 0:
        print(f"  FAILED (exit code {result.returncode})")
        # Print last 15 lines of stderr for debugging
        stderr_lines = result.stderr.strip().split('\n')
        for line in stderr_lines[-15:]:
            print(f"    ERR: {line}")
        return None

    print(f"  COMPLETED in {wall_time:.1f}s ({wall_time/steps:.2f}s per step)")

    # Parse the output metrics CSV
    try:
        import pandas as pd
        df = pd.read_csv(METRICS_CSV)
        metrics = {
            "node_count": node_count,
            "steps": steps,
            "wall_time_s": round(wall_time, 2),
            "time_per_step_s": round(wall_time / steps, 4),
            "avg_reward": round(df["Reward"].mean(), 4),
            "avg_latency_ms": round(df["Latency_ms"].mean(), 4),
            "avg_fidelity_pct": round(df["Fidelity_pct"].mean(), 2),
            "avg_power_w": round(df["Power_W"].mean(), 2),
            "total_migrations": int(df["Migrations"].sum()),
            "total_bytes_mb": round(df["Bytes_cum_MB"].iloc[-1], 4),
            "num_servers": int(df["Num_Nodes"].iloc[0]) if "Num_Nodes" in df.columns else node_count,
            "num_services": len(df),  # == steps
        }
        # Also try to get the actual EdgeServer count from stdout
        for line in result.stdout.split('\n'):
            if 'Starting optimized step' in line and 'services' in line:
                # e.g. "[FedSemGNN-OPT] Starting optimized step 1 with 10 services, 50 servers"
                parts = line.split()
                for j, w in enumerate(parts):
                    if w == 'services,' and j + 1 < len(parts):
                        metrics["actual_servers"] = int(parts[j + 1])
                    if w == 'services,' and j - 1 >= 0:
                        metrics["actual_services"] = int(parts[j - 1])
                break

        print(f"  Reward={metrics['avg_reward']}, Latency={metrics['avg_latency_ms']}ms, "
              f"Power={metrics['avg_power_w']}W, Bytes={metrics['total_bytes_mb']}MB")
        return metrics
    except Exception as e:
        print(f"  ERROR parsing results: {e}")
        # Dump subprocess output for debugging
        stdout_lines = result.stdout.strip().split('\n') if result.stdout else []
        stderr_lines = result.stderr.strip().split('\n') if result.stderr else []
        print(f"  --- Last 20 lines of STDOUT ({len(stdout_lines)} total) ---")
        for line in stdout_lines[-20:]:
            print(f"    OUT: {line}")
        print(f"  --- Last 20 lines of STDERR ({len(stderr_lines)} total) ---")
        for line in stderr_lines[-20:]:
            print(f"    ERR: {line}")
        return None


def main():
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    output_csv = os.path.join(RESULTS_DIR, "scalability_results.csv")

    print("=" * 70)
    print("  FedSemGNN MULTI-SCALE SCALABILITY EXPERIMENT")
    print(f"  Scales: {[s[0] for s in SCALE_CONFIGS]} nodes")
    print(f"  Output: {output_csv}")
    print("=" * 70)

    all_results = []
    for node_count, steps in SCALE_CONFIGS:
        try:
            metrics = run_experiment(node_count, steps,
                                     use_generated_topology=(node_count > 6))
            if metrics:
                all_results.append(metrics)
                # Write intermediate results
                if all_results:
                    keys = all_results[0].keys()
                    with open(output_csv, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=keys)
                        writer.writeheader()
                        writer.writerows(all_results)
                    print(f"  [Saved {len(all_results)} results to {output_csv}]")
            else:
                print(f"  SKIPPING {node_count} nodes (failed)")
                all_results.append({
                    "node_count": node_count,
                    "steps": steps,
                    "wall_time_s": -1,
                    "time_per_step_s": -1,
                    "avg_reward": None,
                    "avg_latency_ms": None,
                    "avg_fidelity_pct": None,
                    "avg_power_w": None,
                    "total_migrations": None,
                    "total_bytes_mb": None,
                    "num_servers": node_count,
                    "num_services": None,
                })
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT at {node_count} nodes — stopping sweep")
            break
        except KeyboardInterrupt:
            print(f"\n  Interrupted — saving {len(all_results)} results")
            break

    # Final save
    if all_results:
        keys = list(all_results[0].keys())
        with open(output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_results)

    print(f"\n{'='*70}")
    print(f"  COMPLETE: {len(all_results)} scale points saved to {output_csv}")
    print(f"{'='*70}")

    # Print summary table
    print(f"\n{'Nodes':>8} {'Steps':>6} {'Time(s)':>8} {'Reward':>8} {'Lat(ms)':>10} {'Power(W)':>10} {'Bytes(MB)':>10}")
    print("-" * 75)
    for r in all_results:
        if r.get("avg_reward") is not None:
            print(f"{r['node_count']:>8} {r['steps']:>6} {r['wall_time_s']:>8.1f} "
                  f"{r['avg_reward']:>8.4f} {r['avg_latency_ms']:>10.4f} "
                  f"{r['avg_power_w']:>10.2f} {r['total_bytes_mb']:>10.4f}")
        else:
            print(f"{r['node_count']:>8} {r['steps']:>6}   FAILED")


if __name__ == "__main__":
    main()
