#!/usr/bin/env python3
"""
Compute convergence speed using proper metric:
Time to reach within X% of steady-state reward (last 200 steps mean).
"""
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

WINDOW = 20  # Smoothing window

print("=" * 80)
print("CONVERGENCE SPEED ANALYSIS (steady-state approach)")
print(f"Method: Timestep where smoothed reward first enters within X% of")
print(f"        steady-state band (mean ± 1 std of last 200 steps)")
print(f"Smoothing window: {WINDOW}")
print("=" * 80)

for name, csvf in algos:
    path = os.path.join(RESULTS, csvf)
    with open(path) as f:
        rows = list(csv.DictReader(f))
    rewards = np.array([float(r["Reward"]) for r in rows])
    
    # Smoothed reward
    smoothed = np.convolve(rewards, np.ones(WINDOW)/WINDOW, mode="valid")
    
    # Steady-state: mean of last 200 smoothed values
    ss_mean = np.mean(smoothed[-200:])
    ss_std = np.std(smoothed[-200:])
    reward_range = np.max(smoothed) - np.min(smoothed)
    
    # Find convergence: first time smoothed enters within 10%, 5%, 1% of reward range to steady state
    results = {}
    for pct_label, pct in [("90%", 0.10), ("95%", 0.05), ("99%", 0.01)]:
        threshold = pct * reward_range if reward_range > 0 else 0.01
        found = -1
        # Find first time smoothed stays within threshold of ss_mean for at least 50 consecutive steps
        for i in range(len(smoothed)):
            if abs(smoothed[i] - ss_mean) <= threshold:
                # Check if it stays within threshold for next 50 steps
                stay = True
                check_len = min(50, len(smoothed) - i)
                for j in range(check_len):
                    if abs(smoothed[i+j] - ss_mean) > threshold * 2:  # Allow 2x for sustained check
                        stay = False
                        break
                if stay:
                    found = i + WINDOW  # Convert back to original timestep
                    break
        results[pct_label] = found
    
    print(f"\n{name}:")
    print(f"  Steady-state reward: {ss_mean:.4f} ± {ss_std:.4f}")
    print(f"  Reward range: {reward_range:.4f}")
    print(f"  90% convergence (within 10% range): step {results['90%']}")
    print(f"  95% convergence (within 5% range):  step {results['95%']}")
    print(f"  99% convergence (within 1% range):  step {results['99%']}")

print("\n" + "=" * 80)
print("Paper claims:")
print("  FedSemGNN: 90% in 32, 95% in 43, 99% in 58")
print("  HierFedPPO: 90% in 115")
print("  FlatFedPPO: 90% in 187") 
print("  HSQF: 90% in 245")
print("=" * 80)

# Also compute a simpler metric: steps until reward stabilizes
# (rolling std drops below 10% of overall std)
print("\n\nSIMPLE STABILIZATION METRIC:")
print("(First step where 50-step rolling std < 10% of overall std)")
print("-" * 60)
for name, csvf in algos:
    path = os.path.join(RESULTS, csvf)
    with open(path) as f:
        rows = list(csv.DictReader(f))
    rewards = np.array([float(r["Reward"]) for r in rows])
    overall_std = np.std(rewards)
    threshold = 0.1 * overall_std if overall_std > 0 else 0.01
    
    # 50-step rolling std
    found = -1
    for i in range(50, len(rewards)):
        window_std = np.std(rewards[i-50:i])
        if window_std < threshold:
            found = i
            break
    print(f"  {name:<18}: stabilizes at step {found} (overall_std={overall_std:.4f}, threshold={threshold:.4f})")
