#!/usr/bin/env python3
"""
Comprehensive experiment runner for FedSemGNN paper.
Runs ALL needed experiments in sequence:
  Phase 1: 6-node / 1000-step — all 6 algorithms (base comparison)
  Phase 2: 100-node / 50-step — all 6 algorithms  
  Phase 3: FedSemGNN scalability sweep (6→25→50→100→200→500→1000 nodes)
  Phase 4: Sensitivity sweeps (tau, ewc, dim, K1, buffer) at 100 nodes / 50 steps
  Phase 5: 200-node / 1000-step — all 6 algorithms (large-scale validation)

Saves all results with proper archiving. Can be left unattended.
"""
import subprocess, os, sys, time, csv, json, shutil
from pathlib import Path

PYTHON = sys.executable
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(PROJECT, "results")

ALGORITHMS = [
    ("FedSemGNN",        "fedsemgnn_metrics.csv",        "src/algorithms/FedSemGNN.py"),
    ("FlatFedPPO",       "flat_fedppo_metrics.csv",       "src/algorithms/flat_fedppo.py"),
    ("HierFedPPO",       "hier_fedppo_metrics.csv",       "src/algorithms/hier_fedppo.py"),
    ("HSQF",             "hsqf_metrics.csv",              "src/algorithms/hsqf.py"),
    ("RandomPlacement",  "random_place_metrics.csv",      "src/algorithms/random_place.py"),
    ("CentralizedPPO",   "centralized_ppo_metrics.csv",   "src/algorithms/centralized_ppo.py"),
]

LOG_FILE = os.path.join(PROJECT, "logs", "comprehensive_run.log")

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def run_single(algo_name, csv_name, steps, nodes, config_override=None, timeout=7200):
    """Run a single algorithm experiment. Returns metrics dict or None."""
    csv_path = os.path.join(RESULTS, csv_name)
    if os.path.exists(csv_path):
        os.remove(csv_path)

    cmd = [PYTHON, os.path.join(PROJECT, "main.py"),
           "--steps", str(steps),
           "--algorithm", algo_name]
    
    if nodes > 6:
        cmd.extend(["--override-num-nodes", str(nodes),
                     "--use-generated-topology",
                     "--topology-mode", "random",
                     "--topology-degree", "8"])
    
    if config_override:
        cfg_path = os.path.join(RESULTS, "_temp_config.json")
        with open(cfg_path, "w") as f:
            json.dump(config_override, f)
        cmd.extend(["--config-override", cfg_path])

    log(f"  Running {algo_name} ({nodes} nodes, {steps} steps)...")

    t0 = time.time()
    try:
        result = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        log(f"  TIMEOUT after {timeout}s for {algo_name}")
        return None
    wall = time.time() - t0

    if result.returncode != 0:
        log(f"  FAILED (exit {result.returncode}) in {wall:.1f}s")
        stderr_tail = result.stderr.strip().split("\n")[-5:]
        for line in stderr_tail:
            log(f"    ERR: {line}")
        return None

    if not os.path.exists(csv_path):
        log(f"  WARNING: {csv_name} not found after run!")
        return None

    # Parse metrics
    csv.field_size_limit(10**7)
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))

    if not rows:
        log(f"  WARNING: {csv_name} is empty!")
        return None

    def safe_floats(col):
        return [float(r[col]) for r in rows if r.get(col) and r[col] != ""]
    def safe_ints(col):
        return [int(float(r[col])) for r in rows if r.get(col) and r[col] != ""]

    lats = safe_floats("Latency_ms")
    fids = safe_floats("Fidelity_pct")
    pows = safe_floats("Power_W")
    rews = safe_floats("Reward")
    migs = safe_ints("Migrations")
    bytes_vals = safe_floats("Bytes_cum_MB")
    nodes_col = safe_ints("Num_Nodes")

    metrics = {
        "algo": algo_name,
        "nodes": nodes_col[0] if nodes_col else nodes,
        "steps": len(rows),
        "wall_s": round(wall, 1),
        "time_per_step": round(wall/len(rows), 3),
        "avg_reward": round(sum(rews)/len(rews), 4) if rews else 0,
        "avg_latency": round(sum(lats)/len(lats), 2) if lats else 0,
        "avg_fidelity": round(sum(fids)/len(fids), 2) if fids else 0,
        "avg_power": round(sum(pows)/len(pows), 2) if pows else 0,
        "total_migrations": sum(migs),
        "total_bytes_mb": round(max(bytes_vals), 4) if bytes_vals else 0,
    }
    
    log(f"  OK ({len(rows)} rows, {wall:.1f}s) Lat={metrics['avg_latency']}ms Fid={metrics['avg_fidelity']}% Pow={metrics['avg_power']}W")
    return metrics


def archive_results(dest_folder, algo_filter=None):
    """Copy current result CSVs to a named archive folder."""
    dest = os.path.join(RESULTS, dest_folder)
    os.makedirs(dest, exist_ok=True)
    for _, csv_name, _ in ALGORITHMS:
        src = os.path.join(RESULTS, csv_name)
        if os.path.exists(src):
            if algo_filter is None or any(a[0] in csv_name for a in algo_filter):
                shutil.copy2(src, os.path.join(dest, csv_name))
    log(f"  Archived results to {dest_folder}/")


def run_phase(phase_name, nodes, steps, dest_folder, algos=None, timeout=7200):
    """Run all algorithms at a given configuration and archive results."""
    log(f"\n{'='*70}")
    log(f"PHASE: {phase_name} ({nodes} nodes, {steps} steps)")
    log(f"{'='*70}")

    if algos is None:
        algos = ALGORITHMS
    
    results = []
    for algo_name, csv_name, _ in algos:
        r = run_single(algo_name, csv_name, steps, nodes, timeout=timeout)
        if r:
            results.append(r)
    
    archive_results(dest_folder)
    
    # Print summary table
    log(f"\n  {'Algorithm':<20} {'Lat(ms)':>10} {'Fid(%)':>8} {'Power(W)':>10} {'Migr':>8} {'Bytes(MB)':>10} {'Time(s)':>8}")
    log(f"  {'-'*76}")
    for r in results:
        log(f"  {r['algo']:<20} {r['avg_latency']:>10.2f} {r['avg_fidelity']:>7.2f}% {r['avg_power']:>10.2f} {r['total_migrations']:>8} {r['total_bytes_mb']:>10.4f} {r['wall_s']:>8.1f}")
    
    return results


def run_scalability_sweep():
    """Run FedSemGNN at multiple node counts for scalability analysis."""
    log(f"\n{'='*70}")
    log(f"PHASE: SCALABILITY SWEEP (FedSemGNN only)")
    log(f"{'='*70}")
    
    # Full 1000-step runs at feasible scales, timing benchmarks at larger scales
    configs = [
        # (nodes, steps, is_full_run)
        (6,     1000, True),
        (25,    200,  True),
        (50,    200,  True),
        (100,   100,  True),
        (200,   50,   True),
        (500,   10,   False),  # timing benchmark
        (1000,  5,    False),  # timing benchmark
    ]
    
    results = []
    dest = os.path.join(RESULTS, "scalability")
    os.makedirs(dest, exist_ok=True)
    
    for nodes, steps, is_full in configs:
        r = run_single("FedSemGNN", "fedsemgnn_metrics.csv", steps, nodes, timeout=3600)
        if r:
            r["is_full_run"] = is_full
            results.append(r)
            # Save individual result
            csv_src = os.path.join(RESULTS, "fedsemgnn_metrics.csv")
            if os.path.exists(csv_src):
                shutil.copy2(csv_src, os.path.join(dest, f"fedsemgnn_{nodes}node_{steps}step.csv"))
    
    # Save scalability summary
    summary_path = os.path.join(dest, "scalability_results.csv")
    if results:
        keys = list(results[0].keys())
        with open(summary_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(results)
    
    log(f"\n  {'Nodes':>8} {'Steps':>6} {'Time/step':>10} {'Lat(ms)':>10} {'Fid(%)':>8} {'Power(W)':>10}")
    log(f"  {'-'*58}")
    for r in results:
        log(f"  {r['nodes']:>8} {r['steps']:>6} {r['time_per_step']:>10.3f} {r['avg_latency']:>10.2f} {r['avg_fidelity']:>7.2f}% {r['avg_power']:>10.2f}")
    
    return results


def run_sensitivity_sweeps():
    """Run all sensitivity experiments (tau, ewc, dim, K1, buffer)."""
    log(f"\n{'='*70}")
    log(f"PHASE: SENSITIVITY SWEEPS (100 nodes, 50 steps)")
    log(f"{'='*70}")
    
    SWEEP_NODES = 100
    SWEEP_STEPS = 50
    
    sweeps = {
        "tau": [
            ("tau_0.2", {"semantic_threshold": 0.2, "ewc_lambda": 0.4}),
            ("tau_0.3", {"semantic_threshold": 0.3, "ewc_lambda": 0.4}),
            ("tau_0.4", {"semantic_threshold": 0.4, "ewc_lambda": 0.4}),
        ],
        "ewc": [
            ("ewc_0.0", {"semantic_threshold": 0.3, "ewc_lambda": 0.0}),
            ("ewc_0.4", {"semantic_threshold": 0.3, "ewc_lambda": 0.4}),
            ("ewc_0.8", {"semantic_threshold": 0.3, "ewc_lambda": 0.8}),
        ],
        "dim": [
            ("dim_8",  {"semantic_dim": 8}),
            ("dim_16", {"semantic_dim": 16}),
            ("dim_32", {"semantic_dim": 32}),
        ],
        "k1": [
            ("k1_5",  {"local_sync_interval": 5}),
            ("k1_10", {"local_sync_interval": 10}),
            ("k1_20", {"local_sync_interval": 20}),
        ],
        "buffer": [
            ("buf_10k", {"replay_buffer_capacity": 10000}),
            ("buf_20k", {"replay_buffer_capacity": 20000}),
            ("buf_40k", {"replay_buffer_capacity": 40000}),
        ],
    }
    
    all_results = []
    for sweep_name, configs in sweeps.items():
        log(f"\n  --- Sweep: {sweep_name} ---")
        for run_name, cfg in configs:
            # Save config
            cfg_dir = os.path.join(RESULTS, "sensitivity", run_name)
            os.makedirs(cfg_dir, exist_ok=True)
            with open(os.path.join(cfg_dir, "config.json"), "w") as f:
                json.dump(cfg, f)
            
            r = run_single("FedSemGNN", "fedsemgnn_metrics.csv", 
                          SWEEP_STEPS, SWEEP_NODES, 
                          config_override=cfg, timeout=600)
            if r:
                r["sweep"] = sweep_name
                r["run_name"] = run_name
                r["config"] = cfg
                all_results.append(r)
                # Save metrics CSV
                src = os.path.join(RESULTS, "fedsemgnn_metrics.csv")
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(cfg_dir, "fedsemgnn_metrics.csv"))
    
    # Save sensitivity summary
    summary_path = os.path.join(RESULTS, "sensitivity", "sensitivity_summary.csv")
    if all_results:
        keys = ["sweep", "run_name", "avg_latency", "avg_fidelity", "avg_power", "avg_reward", "total_migrations", "total_bytes_mb", "wall_s"]
        with open(summary_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(all_results)
    
    log(f"\n  {'Sweep':<10} {'Name':<10} {'Lat(ms)':>10} {'Fid(%)':>8} {'Power(W)':>10}")
    log(f"  {'-'*50}")
    for r in all_results:
        log(f"  {r['sweep']:<10} {r['run_name']:<10} {r['avg_latency']:>10.2f} {r['avg_fidelity']:>7.2f}% {r['avg_power']:>10.2f}")
    
    return all_results


def main():
    total_start = time.time()
    log(f"\n{'#'*70}")
    log(f"# COMPREHENSIVE EXPERIMENT RUNNER — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"# Python: {PYTHON}")
    log(f"# Project: {PROJECT}")
    log(f"{'#'*70}")
    
    all_phase_results = {}
    
    # Phase 1: 6 nodes / 1000 steps — baseline comparison (for Table 2)
    phase1 = run_phase("Base Comparison (6 nodes, 1000 steps)", 
                       nodes=6, steps=1000, dest_folder="6node_1000step")
    all_phase_results["6node_1000step"] = phase1
    
    # Phase 2: 100 nodes / 50 steps — all algorithms (medium scale)
    phase2 = run_phase("Medium Scale (100 nodes, 50 steps)",
                       nodes=100, steps=50, dest_folder="100node_50step")
    all_phase_results["100node_50step"] = phase2
    
    # Phase 3: Scalability sweep (FedSemGNN only)
    phase3 = run_scalability_sweep()
    all_phase_results["scalability"] = phase3
    
    # Phase 4: Sensitivity sweeps
    phase4 = run_sensitivity_sweeps()
    all_phase_results["sensitivity"] = phase4
    
    # Phase 5: 200 nodes / 1000 steps — large scale if time permits
    elapsed = time.time() - total_start
    remaining = (5*3600) - elapsed  # 5 hours budget
    if remaining > 3600:  # Only if >1hr remaining
        phase5 = run_phase("Large Scale (200 nodes, 1000 steps)",
                           nodes=200, steps=1000, dest_folder="200node_1000step",
                           timeout=int(remaining/6))
        all_phase_results["200node_1000step"] = phase5
    else:
        log(f"\n  Skipping 200-node/1000-step phase (only {remaining/60:.0f} min remaining)")
    
    total_time = time.time() - total_start
    log(f"\n{'#'*70}")
    log(f"# ALL PHASES COMPLETE in {total_time/60:.1f} minutes ({total_time/3600:.1f} hours)")
    log(f"{'#'*70}")
    
    # Save master summary
    summary_path = os.path.join(RESULTS, "comprehensive_summary.json")
    try:
        with open(summary_path, "w") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_time_s": round(total_time, 1),
                "phases": {k: len(v) for k, v in all_phase_results.items()},
            }, f, indent=2)
    except Exception as e:
        log(f"  Warning: Could not save summary: {e}")


if __name__ == "__main__":
    main()
