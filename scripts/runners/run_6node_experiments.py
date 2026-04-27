"""Run all 6 algorithms at 6 nodes (base scale) for the main paper comparison."""
import subprocess
import sys
import os
import time
import shutil

PYTHON = os.path.join('.venv', 'Scripts', 'python.exe')
STEPS = 1000
RESULTS_DIR = 'results'
OUTPUT_DIR = os.path.join(RESULTS_DIR, '6node_results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Algorithm configurations (6 nodes = base dataset, no override needed)
ALGORITHMS = [
    {
        'name': 'RandomPlacement',
        'script': 'src/algorithms/random_place.py',
        'args': ['--steps', str(STEPS)],
        'output': 'random_place_metrics.csv',
    },
    {
        'name': 'HSQF',
        'script': 'src/algorithms/hsqf.py',
        'args': ['--steps', str(STEPS)],
        'output': 'hsqf_metrics.csv',
    },
    {
        'name': 'FlatFedPPO',
        'script': 'src/algorithms/flat_fedppo.py',
        'args': ['--steps', str(STEPS)],
        'output': 'flat_fedppo_metrics.csv',
    },
    {
        'name': 'CentralizedPPO',
        'script': 'src/algorithms/centralized_ppo.py',
        'args': ['--steps', str(STEPS)],
        'output': 'centralized_ppo_metrics.csv',
    },
    {
        'name': 'HierFedPPO',
        'script': 'src/algorithms/hier_fedppo.py',
        'args': ['--steps', str(STEPS)],
        'output': 'hier_fedppo_metrics.csv',
    },
    {
        'name': 'FedSemGNN',
        'script': 'src/algorithms/FedSemGNN.py',
        'args': ['--steps', str(STEPS)],
        'output': 'fedsemgnn_metrics.csv',
    },
]

total_start = time.time()
for algo in ALGORITHMS:
    print(f"\n{'='*60}")
    print(f"Running {algo['name']} at 6 nodes...")
    print(f"{'='*60}")
    
    cmd = [PYTHON, algo['script']] + algo['args']
    start = time.time()
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    elapsed = time.time() - start
    
    if result.returncode != 0:
        print(f"{algo['name']}: FAILED (code {result.returncode}) in {elapsed:.1f}s")
        continue
    
    # Copy result to 6node_results folder
    src = os.path.join(RESULTS_DIR, algo['output'])
    dst = os.path.join(OUTPUT_DIR, algo['output'])
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"{algo['name']}: SUCCESS in {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"Copied to {dst}")
    else:
        print(f"{algo['name']}: COMPLETED but output file {src} not found!")

total_elapsed = time.time() - total_start
print(f"\n{'='*60}")
print(f"ALL DONE. Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
print(f"Results saved in: {OUTPUT_DIR}")
