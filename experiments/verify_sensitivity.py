#!/usr/bin/env python3
"""Verify sensitivity CSV data - compute per-step mean±std for all configs."""
import csv, os, statistics

base = "results/sensitivity"
configs = [
    ("tau_0.2", "tau_0.2"), ("tau_0.3", "tau_0.3"), ("tau_0.4", "tau_0.4"),
    ("ewc_0.0", "ewc_0.0"), ("ewc_0.4", "ewc_0.4"), ("ewc_0.8", "ewc_0.8"),
    ("dim_8", "dim_8"), ("dim_16", "dim_16"), ("dim_32", "dim_32"),
    ("k1_5", "k1_5"), ("k1_10", "k1_10"), ("k1_20", "k1_20"),
    ("buf_10k", "buf_10k"), ("buf_20k", "buf_20k"), ("buf_40k", "buf_40k"),
]

print(f"{'Config':<12} {'Lat mean':>10} {'Lat std':>10} {'Fid mean':>10} {'Fid std':>10} {'Power mean':>12} {'N':>4}")
print("-" * 72)

for name, folder in configs:
    csv_path = os.path.join(base, folder, "fedsemgnn_metrics.csv")
    if not os.path.exists(csv_path):
        print(f"{name:<12} NOT FOUND")
        continue
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    lats = [float(r["Latency_ms"]) for r in rows if r.get("Latency_ms")]
    fids = [float(r["Fidelity_pct"]) for r in rows if r.get("Fidelity_pct")]
    pows = [float(r["Power_W"]) for r in rows if r.get("Power_W")]
    
    lat_m = statistics.mean(lats) if lats else 0
    lat_s = statistics.stdev(lats) if len(lats) > 1 else 0
    fid_m = statistics.mean(fids) if fids else 0
    fid_s = statistics.stdev(fids) if len(fids) > 1 else 0
    pow_m = statistics.mean(pows) if pows else 0
    
    print(f"{name:<12} {lat_m:>10.2f} {lat_s:>10.2f} {fid_m:>10.2f} {fid_s:>10.2f} {pow_m:>12.2f} {len(rows):>4}")
