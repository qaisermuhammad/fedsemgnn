#!/usr/bin/env python3
"""
Multi-trial experiment runner for statistically sound results.
Runs each algorithm N times at 6 nodes / 1000 steps to get mean ± std.
The paper claims "5 independent trials" so we run 5 per algorithm.
"""
import subprocess, os, sys, time, csv, json, shutil, statistics
from pathlib import Path

PYTHON = sys.executable
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(PROJECT, "results")
TRIALS_DIR = os.path.join(RESULTS, "multi_trial")

N_TRIALS = 5
STEPS = 1000
NODES = 6

ALGORITHMS = [
    ("FedSemGNN",       "fedsemgnn_metrics.csv"),
    ("FlatFedPPO",      "flat_fedppo_metrics.csv"),
    ("HierFedPPO",      "hier_fedppo_metrics.csv"),
    ("HSQF",            "hsqf_metrics.csv"),
    ("RandomPlacement", "random_place_metrics.csv"),
    ("CentralizedPPO",  "centralized_ppo_metrics.csv"),
]

LOG_FILE = os.path.join(PROJECT, "logs", "multi_trial_run.log")

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def parse_csv(csv_path):
    """Parse a metrics CSV and return summary dict."""
    csv.field_size_limit(10**7)
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    
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
    
    return {
        "rows": len(rows),
        "avg_latency": sum(lats)/len(lats) if lats else 0,
        "avg_fidelity": sum(fids)/len(fids) if fids else 0,
        "avg_power": sum(pows)/len(pows) if pows else 0,
        "avg_reward": sum(rews)/len(rews) if rews else 0,
        "total_migrations": sum(migs),
        "total_bytes_mb": max(bytes_vals) if bytes_vals else 0,
    }


def run_trial(algo_name, csv_name, trial_num, seed=None):
    """Run a single trial."""
    csv_path = os.path.join(RESULTS, csv_name)
    if os.path.exists(csv_path):
        os.remove(csv_path)
    
    cmd = [PYTHON, os.path.join(PROJECT, "main.py"),
           "--steps", str(STEPS),
           "--algorithm", algo_name]
    
    env = os.environ.copy()
    if seed is not None:
        env["FEDSEMGNN_SEED"] = str(seed)
    
    t0 = time.time()
    result = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True, 
                          timeout=7200, env=env)
    wall = time.time() - t0
    
    if result.returncode != 0 or not os.path.exists(csv_path):
        log(f"    Trial {trial_num}: FAILED ({wall:.1f}s)")
        return None
    
    metrics = parse_csv(csv_path)
    metrics["trial"] = trial_num
    metrics["wall_s"] = round(wall, 1)
    
    # Archive this trial's CSV
    trial_dir = os.path.join(TRIALS_DIR, algo_name.lower())
    os.makedirs(trial_dir, exist_ok=True)
    shutil.copy2(csv_path, os.path.join(trial_dir, f"trial_{trial_num}.csv"))
    
    log(f"    Trial {trial_num}: Lat={metrics['avg_latency']:.2f}ms Fid={metrics['avg_fidelity']:.2f}% Pow={metrics['avg_power']:.1f}W ({wall:.1f}s)")
    return metrics


def compute_stats(trials, key):
    """Compute mean and std for a key across trials."""
    vals = [t[key] for t in trials if t is not None]
    if not vals:
        return 0, 0
    mean = statistics.mean(vals)
    std = statistics.stdev(vals) if len(vals) > 1 else 0
    return mean, std


def main():
    total_start = time.time()
    log(f"\n{'#'*70}")
    log(f"# MULTI-TRIAL EXPERIMENT RUNNER — {N_TRIALS} trials per algorithm")
    log(f"# Config: {NODES} nodes, {STEPS} steps")
    log(f"{'#'*70}")
    
    os.makedirs(TRIALS_DIR, exist_ok=True)
    all_summaries = []
    
    for algo_name, csv_name in ALGORITHMS:
        log(f"\n{'='*60}")
        log(f"  {algo_name} — {N_TRIALS} trials")
        log(f"{'='*60}")
        
        trials = []
        for trial in range(1, N_TRIALS + 1):
            r = run_trial(algo_name, csv_name, trial, seed=42+trial)
            if r:
                trials.append(r)
        
        if trials:
            lat_mean, lat_std = compute_stats(trials, "avg_latency")
            fid_mean, fid_std = compute_stats(trials, "avg_fidelity")
            pow_mean, pow_std = compute_stats(trials, "avg_power")
            rew_mean, rew_std = compute_stats(trials, "avg_reward")
            mig_mean, mig_std = compute_stats(trials, "total_migrations")
            byt_mean, byt_std = compute_stats(trials, "total_bytes_mb")
            
            summary = {
                "algo": algo_name,
                "n_trials": len(trials),
                "lat_mean": round(lat_mean, 2),
                "lat_std": round(lat_std, 2),
                "fid_mean": round(fid_mean, 2),
                "fid_std": round(fid_std, 2),
                "pow_mean": round(pow_mean, 2),
                "pow_std": round(pow_std, 2),
                "rew_mean": round(rew_mean, 4),
                "rew_std": round(rew_std, 4),
                "mig_mean": round(mig_mean, 0),
                "mig_std": round(mig_std, 0),
                "byt_mean": round(byt_mean, 4),
                "byt_std": round(byt_std, 4),
            }
            all_summaries.append(summary)
            
            log(f"\n  {algo_name} SUMMARY ({len(trials)} trials):")
            log(f"    Latency:    {lat_mean:.2f} ± {lat_std:.2f} ms")
            log(f"    Fidelity:   {fid_mean:.2f} ± {fid_std:.2f} %")
            log(f"    Power:      {pow_mean:.1f} ± {pow_std:.1f} W")
            log(f"    Reward:     {rew_mean:.4f} ± {rew_std:.4f}")
            log(f"    Migrations: {mig_mean:.0f} ± {mig_std:.0f}")
            log(f"    Bytes:      {byt_mean:.4f} ± {byt_std:.4f} MB")
    
    # Save comprehensive summary
    summary_path = os.path.join(TRIALS_DIR, "multi_trial_summary.csv")
    if all_summaries:
        keys = list(all_summaries[0].keys())
        with open(summary_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(all_summaries)
    
    total_time = time.time() - total_start
    log(f"\n{'#'*70}")
    log(f"# MULTI-TRIAL COMPLETE in {total_time/60:.1f} minutes")
    log(f"# Results saved to {summary_path}")
    log(f"{'#'*70}")
    
    # Print final comparison table
    log(f"\n{'Algorithm':<20} {'Latency(ms)':<16} {'Fidelity(%)':<16} {'Power(W)':<16} {'Migrations':<16} {'Bytes(MB)':<16}")
    log(f"{'-'*96}")
    for s in all_summaries:
        log(f"{s['algo']:<20} {s['lat_mean']:>6.2f}±{s['lat_std']:<6.2f}  {s['fid_mean']:>6.2f}±{s['fid_std']:<6.2f}  {s['pow_mean']:>7.1f}±{s['pow_std']:<6.1f}  {s['mig_mean']:>7.0f}±{s['mig_std']:<6.0f}  {s['byt_mean']:>6.4f}±{s['byt_std']:<6.4f}")


if __name__ == "__main__":
    main()
