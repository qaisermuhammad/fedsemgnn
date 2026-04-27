"""Run all 6 algorithms at 200 nodes with generated topology (1000 steps each)."""
import subprocess
import sys
import os
import time
import shutil

PYTHON = sys.executable
STEPS = 1000
NODES = 200

# Save the 6-node results first
BACKUP_DIR = "results/6node_backup"
os.makedirs(BACKUP_DIR, exist_ok=True)
for f in [
    "fedsemgnn_metrics.csv",
    "flat_fedppo_metrics.csv",
    "hier_fedppo_metrics.csv",
    "hsqf_metrics.csv",
    "random_place_metrics.csv",
    "centralized_ppo_metrics.csv",
]:
    src = os.path.join("results", f)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(BACKUP_DIR, f))
        print(f"Backed up {f}")

# Algorithm scripts
ALGORITHMS = [
    ("RandomPlacement", "src/algorithms/random_place.py"),
    ("HSQF",           "src/algorithms/hsqf.py"),
    ("FlatFedPPO",     "src/algorithms/flat_fedppo.py"),
    ("CentralizedPPO", "src/algorithms/flat_fedppo.py"),  # with FEDSEMGNN_CENTRALIZED=true
    ("HierFedPPO",     "src/algorithms/hier_fedppo.py"),
    ("FedSemGNN",      "src/algorithms/FedSemGNN.py"),
]

results_dir = f"results/{NODES}node_results"
os.makedirs(results_dir, exist_ok=True)

total_start = time.time()
for algo_name, script in ALGORITHMS:
    print(f"\n{'='*70}")
    print(f"Running {algo_name} at {NODES} nodes, {STEPS} steps")
    print(f"{'='*70}")
    
    env = os.environ.copy()
    if algo_name == "CentralizedPPO":
        env["FEDSEMGNN_CENTRALIZED"] = "true"
    
    cmd = [
        PYTHON, script,
        "--steps", str(STEPS),
        "--override-num-nodes", str(NODES),
        "--use-generated-topology",
        "--topology-mode", "random",
        "--topology-degree", "8",
    ]
    
    start = time.time()
    result = subprocess.run(cmd, env=env, timeout=7200)
    elapsed = time.time() - start
    
    status = "SUCCESS" if result.returncode == 0 else f"FAILED (code {result.returncode})"
    print(f"{algo_name}: {status} in {elapsed:.1f}s ({elapsed/60:.1f} min)")
    
    # Copy the result CSV to the 200-node results directory
    csv_map = {
        "RandomPlacement": "random_place_metrics.csv",
        "HSQF":           "hsqf_metrics.csv",
        "FlatFedPPO":     "flat_fedppo_metrics.csv",
        "CentralizedPPO": "centralized_ppo_metrics.csv",
        "HierFedPPO":     "hier_fedppo_metrics.csv",
        "FedSemGNN":      "fedsemgnn_metrics.csv",
    }
    src_csv = os.path.join("results", csv_map[algo_name])
    if os.path.exists(src_csv):
        dst_csv = os.path.join(results_dir, csv_map[algo_name])
        shutil.copy2(src_csv, dst_csv)
        print(f"Copied to {dst_csv}")

total_elapsed = time.time() - total_start
print(f"\n{'='*70}")
print(f"ALL DONE. Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
print(f"Results saved in: {results_dir}")
print(f"6-node backups in: {BACKUP_DIR}")
