#!/usr/bin/env python3
"""Re-run all 6 algorithms at 6 nodes, 1000 steps for Table 2 data."""
import subprocess, os, sys, time, csv

PYTHON = sys.executable
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT, "results")

ALGORITHMS = [
    ("FedSemGNN",       "fedsemgnn_metrics.csv"),
    ("FlatFedPPO",      "flat_fedppo_metrics.csv"),
    ("HierFedPPO",      "hier_fedppo_metrics.csv"),
    ("HSQF",            "hsqf_metrics.csv"),
    ("RandomPlacement",  "random_place_metrics.csv"),
    ("CentralizedPPO",  "centralized_ppo_metrics.csv"),
]

STEPS = 1000

def run_algorithm(algo_name, csv_name):
    csv_path = os.path.join(RESULTS_DIR, csv_name)
    if os.path.exists(csv_path):
        os.remove(csv_path)
        print(f"  Deleted old {csv_name}")

    cmd = [PYTHON, os.path.join(PROJECT, "main.py"),
           "--steps", str(STEPS), "--algorithm", algo_name]
    print(f"  CMD: {' '.join(cmd)}")

    t0 = time.time()
    result = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True, timeout=7200)
    wall = time.time() - t0

    if result.returncode != 0:
        print(f"  FAILED (exit {result.returncode}) in {wall:.1f}s")
        for line in result.stderr.strip().split("\n")[-10:]:
            print(f"    ERR: {line}")
        return None

    if not os.path.exists(csv_path):
        print(f"  WARNING: CSV not found after run!")
        return None

    csv.field_size_limit(10**7)
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))

    powers = [float(r["Power_W"]) for r in rows if r.get("Power_W") and r["Power_W"] != ""]
    lats   = [float(r["Latency_ms"]) for r in rows if r.get("Latency_ms") and r["Latency_ms"] != ""]
    rews   = [float(r["Reward"]) for r in rows if r.get("Reward") and r["Reward"] != ""]
    fids   = [float(r["Fidelity_pct"]) for r in rows if r.get("Fidelity_pct") and r["Fidelity_pct"] != ""]
    migs   = [int(float(r["Migrations"])) for r in rows if r.get("Migrations") and r["Migrations"] != ""]

    # Communication
    bytes_cols = [r.get("Bytes_cum_MB") or r.get("Bytes_Cum_MB") or r.get("CumBytes_MB") for r in rows]
    bytes_vals = [float(b) for b in bytes_cols if b and b != ""]
    total_bytes = max(bytes_vals) if bytes_vals else 0.0

    avg_p = sum(powers)/len(powers) if powers else 0
    avg_l = sum(lats)/len(lats) if lats else 0
    avg_r = sum(rews)/len(rews) if rews else 0
    avg_f = sum(fids)/len(fids) if fids else 0
    total_m = sum(migs)

    print(f"  OK ({len(rows)} rows, {wall:.1f}s)")
    print(f"    Reward={avg_r:.4f} Power={avg_p:.2f}W Latency={avg_l:.4f}ms Fidelity={avg_f:.1f}% Migrations={total_m} Bytes={total_bytes:.4f}MB")

    return {
        "algo": algo_name, "rows": len(rows), "wall_s": wall,
        "avg_reward": avg_r, "avg_power": avg_p, "avg_latency": avg_l,
        "avg_fidelity": avg_f, "total_migrations": total_m,
        "total_bytes_mb": total_bytes,
    }


if __name__ == "__main__":
    results = []
    t_total = time.time()

    for algo_name, csv_name in ALGORITHMS:
        print(f"\n{'='*60}")
        print(f"Running {algo_name} ({STEPS} steps, 6 nodes)")
        print(f"{'='*60}")
        r = run_algorithm(algo_name, csv_name)
        if r:
            results.append(r)

    print(f"\n\n{'='*70}")
    print(f"ALL ALGORITHMS COMPLETE ({time.time()-t_total:.0f}s total)")
    print(f"{'='*70}")
    print(f"{'Algorithm':<20} {'Reward':>8} {'Power(W)':>10} {'Latency(ms)':>12} {'Fidelity':>8} {'Migr':>8} {'Bytes(MB)':>10}")
    print("-"*70)
    for r in results:
        print(f"{r['algo']:<20} {r['avg_reward']:>8.4f} {r['avg_power']:>10.2f} {r['avg_latency']:>12.4f} {r['avg_fidelity']:>7.1f}% {r['total_migrations']:>8d} {r['total_bytes_mb']:>10.4f}")
