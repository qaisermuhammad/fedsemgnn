#!/usr/bin/env python3
"""Verify convergence speed claims against actual trial data."""
import csv, sys, os
import numpy as np
csv.field_size_limit(10**7)

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(PROJECT, "results")

algos = [
    ("FedSemGNN", "fedsemgnn_metrics.csv"),
    ("FlatFedPPO", "flat_fedppo_metrics.csv"),
    ("HierFedPPO", "hier_fedppo_metrics.csv"),
    ("HSQF", "hsqf_metrics.csv"),
    ("RandomPlacement", "random_place_metrics.csv"),
    ("CentralizedPPO", "centralized_ppo_metrics.csv"),
]

WINDOW = 50

print("=" * 70)
print("CONVERGENCE SPEED ANALYSIS")
print(f"Window: {WINDOW}-step rolling average")
print("=" * 70)

header = f"{'Algo':<18} {'FinalRew':>10} {'90%_step':>10} {'95%_step':>10} {'99%_step':>10}"
print(header)
print("-" * len(header))

for name, csvf in algos:
    path = os.path.join(RESULTS, csvf)
    with open(path) as f:
        rows = list(csv.DictReader(f))
    
    rewards = np.array([float(r["Reward"]) for r in rows])
    
    # Rolling average
    smoothed = np.convolve(rewards, np.ones(WINDOW)/WINDOW, mode="valid")
    final_reward = smoothed[-1]
    
    results = {}
    for pct_label, pct in [("90%", 0.9), ("95%", 0.95), ("99%", 0.99)]:
        target = pct * final_reward
        found = -1
        for i, v in enumerate(smoothed):
            if final_reward > 0 and v >= target:
                found = i + WINDOW
                break
            elif final_reward <= 0 and v <= target:
                found = i + WINDOW
                break
        results[pct_label] = found
    
    print(f"{name:<18} {final_reward:>10.4f} {results['90%']:>10} {results['95%']:>10} {results['99%']:>10}")

print("\n" + "=" * 70)
print("Paper claims:")
print("  FedSemGNN: 90% in 32, 95% in 43, 99% in 58")
print("  HierFedPPO: 90% in 115")
print("  FlatFedPPO: 90% in 187")
print("  HSQF: 90% in 245")
print("=" * 70)
