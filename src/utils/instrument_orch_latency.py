#!/usr/bin/env python3
# instrument_orch_latency.py

import time
import csv
import os
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION ---
OUT_DIR    = "results/processed"
CSV_PATH   = os.path.join(OUT_DIR, "orch_latency.csv")
HIST_PNG   = os.path.join(OUT_DIR, "orch_latency_hist.png")

TOTAL_STEPS = 500   # ← set to your simulation length
# ----------------------

# TODO: replace with your real imports
# from your_project.orchestrator import EdgeOrchestrator
# from your_project.simulation    import get_state

class FakeOrchestrator:
    """Stub: replace with your real orchestrator."""
    def __init__(self):
        pass
    def assign(self, state):
        # simulate compute work
        time.sleep(0.001)
        return [0]*len(state)

def get_state(step):
    """
    Stub: return the semantic+feature vector your orchestrator consumes
    for this simulation step. E.g. a list of size N_SERVICES of sem_0…sem_15.
    """
    return np.random.rand(100,16)  # dummy

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Init your orchestrator
    # orch = EdgeOrchestrator(...)
    orch = FakeOrchestrator()

    # Prepare CSV
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Step","StartTime","EndTime","Duration_ms"])

        # Loop through each simulation step
        for step in range(TOTAL_STEPS):
            state = get_state(step)

            start = time.time()
            assignments = orch.assign(state)
            end   = time.time()

            dur_ms = (end - start)*1000
            writer.writerow([step, start, end, dur_ms])

    print(f"✅ Logged orchestration latency to {CSV_PATH}")

    # --- Plot histogram ---
    df = np.loadtxt(CSV_PATH, delimiter=",", skiprows=1, usecols=3)
    plt.figure(figsize=(6,4))
    plt.hist(df, bins=30, color="#2c7fb8", edgecolor="white")
    plt.xlabel("Orchestrator latency (ms)")
    plt.ylabel("Count")
    plt.title("Per-Step Orchestration Latency Distribution")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(HIST_PNG, dpi=500)
    plt.show()
    plt.close()
    print(f"✅ Saved latency histogram to {HIST_PNG}")

if __name__ == "__main__":
    main()
