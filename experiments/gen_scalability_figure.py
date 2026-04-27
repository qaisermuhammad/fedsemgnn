#!/usr/bin/env python3
"""
Generate the 2x2 scalability analysis figure from REAL experiment data.
Uses verified scalability_results.csv from run_comprehensive.py.

Data sources (from run_comprehensive.py 2026-02-28):
  - 6 nodes / 1000 steps (full experiment)
  - 25-50 nodes / 200 steps (full experiments)
  - 100 nodes / 100 steps (full experiment)
  - 200 nodes / 50 steps (full experiment)
  - 500-1000 nodes / 5-10 steps (timing benchmarks)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# ---------- VERIFIED DATA from run_comprehensive.py (2026-02-28) ----------
# Format: (nodes, latency_ms, time_per_step_s, fidelity_pct, is_full_run)
REAL_DATA = [
    (6,    27.94, 0.052, 99.98,  True),   # 1000 steps
    (25,   31.40, 0.059, 100.0,  True),   # 200 steps
    (50,   29.83, 0.091, 100.0,  True),   # 200 steps
    (100,  30.61, 0.179, 100.0,  True),   # 100 steps
    (200,  31.00, 0.459, 100.0,  True),   # 50 steps
    (500,  31.24, 1.926, 100.0,  False),  # 10 steps (timing)
    (1000, 31.32, 6.142, 100.0,  False),  # 5 steps (timing)
]

# Try loading from CSV if available (overrides hardcoded data)
SCALABILITY_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "results", "scalability", "scalability_results.csv"
)
if os.path.exists(SCALABILITY_CSV):
    loaded = []
    with open(SCALABILITY_CSV) as f:
        for row in csv.DictReader(f):
            if row.get("avg_latency") and float(row["avg_latency"]) > 0:
                loaded.append((
                    int(row["nodes"]),
                    float(row["avg_latency"]),
                    float(row["time_per_step"]),
                    float(row["avg_fidelity"]),
                    str(row.get("is_full_run", "True")).strip() == "True",
                ))
    if loaded:
        REAL_DATA = loaded
        print(f"Loaded {len(loaded)} data points from {SCALABILITY_CSV}")

nodes      = np.array([d[0] for d in REAL_DATA])
latency    = np.array([d[1] for d in REAL_DATA])
time_step  = np.array([d[2] for d in REAL_DATA])
fidelity   = np.array([d[3] for d in REAL_DATA])
is_full    = np.array([d[4] for d in REAL_DATA])

# Log-log regression for computation time
log_n = np.log10(nodes)
log_t = np.log10(time_step)
slope_t, intercept_t = np.polyfit(log_n, log_t, 1)

# ===================== FIGURE =====================
fig, axes = plt.subplots(2, 2, figsize=(12, 9))

# --- 1) Latency vs Nodes ---
ax = axes[0, 0]
full_mask = is_full
timing_mask = ~is_full
if full_mask.any():
    ax.semilogx(nodes[full_mask], latency[full_mask], "bo-", markersize=8,
                linewidth=2, label="Full experiment", zorder=3)
if timing_mask.any():
    ax.semilogx(nodes[timing_mask], latency[timing_mask], "b^--", markersize=8,
                linewidth=1.5, alpha=0.6, label="Timing benchmark", zorder=2)
mean_lat_25p = np.mean(latency[nodes >= 25])
ax.axhline(y=mean_lat_25p, color="red", linestyle=":", alpha=0.5,
           label=f"Mean (≥25 nodes) = {mean_lat_25p:.1f} ms")
ax.set_xlabel("Number of Nodes", fontsize=12)
ax.set_ylabel("Orchestration Latency (ms)", fontsize=12)
ax.set_title("Latency Stability Across Scales", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_ylim(0, max(latency) * 1.5)

# --- 2) Semantic Fidelity vs Nodes ---
ax = axes[0, 1]
if full_mask.any():
    ax.semilogx(nodes[full_mask], fidelity[full_mask], "gs-", markersize=10,
                linewidth=2, label="Full experiment", zorder=3)
if timing_mask.any():
    ax.semilogx(nodes[timing_mask], fidelity[timing_mask], "g^--", markersize=10,
                linewidth=1.5, alpha=0.6, label="Timing benchmark", zorder=2)
ax.fill_between(nodes, 95, 100, alpha=0.1, color="green")
ax.set_xlabel("Number of Nodes", fontsize=12)
ax.set_ylabel("Semantic Fidelity (%)", fontsize=12)
ax.set_title("Semantic Fidelity Across Scales", fontsize=13, fontweight="bold")
ax.set_ylim(90, 101)
ax.grid(True, alpha=0.3)
ax.text(np.sqrt(nodes.min() * nodes.max()), 96,
        f"~100% at all {len(nodes)} scale points",
        fontsize=11, color="green", ha="center")
ax.legend(fontsize=10)

# --- 3) Computation Time per Step (log-log) ---
ax = axes[1, 0]
ax.loglog(nodes, time_step, "rd-", markersize=8, linewidth=2, label="Measured")
fit_t = 10 ** (intercept_t + slope_t * log_n)
ax.loglog(nodes, fit_t, "b--", linewidth=1.5, alpha=0.7,
          label=f"Fit (slope={slope_t:.3f})")
# O(N) reference line through first point
ax.loglog(nodes, time_step[0] * (nodes / nodes[0]), "k:", linewidth=1, alpha=0.4,
          label="O(N) reference")
ax.set_xlabel("Number of Nodes", fontsize=12)
ax.set_ylabel("Time per Step (s)", fontsize=12)
ax.set_title(f"Computation Time (log-log slope = {slope_t:.3f})",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# --- 4) Scale Factor vs Key Metrics ---
ax = axes[1, 1]
scale_factor = nodes / nodes[0]
lat_ratio = latency / latency[0]
time_ratio = time_step / time_step[0]

ax.loglog(scale_factor, time_ratio, "rd-", markersize=8, linewidth=2,
          label="Computation time ratio")
ax.loglog(scale_factor, lat_ratio, "b^-", markersize=8, linewidth=2,
          label="Latency ratio")
ax.loglog(scale_factor, scale_factor, "k:", linewidth=1, alpha=0.4,
          label="Linear scaling O(N)")
ax.set_xlabel("Scale Factor (×)", fontsize=12)
ax.set_ylabel("Metric Ratio (×)", fontsize=12)
ax.set_title("Scaling Behavior Summary", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()

# Save to both graphs/ and figures/
for outdir in ["graphs", "figures"]:
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, "scalability_analysis.png")
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    print(f"Saved {outpath}")
plt.close()
print("Done!")
