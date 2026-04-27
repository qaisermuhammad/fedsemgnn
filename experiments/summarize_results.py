#summarize_results.py


#!/usr/bin/env python3
import glob, os
import pandas as pd

records = []
for path in glob.glob("results/*_*_*steps/fedsemgnn_metrics.csv"):
    df = pd.read_csv(path)
    if "Fidelity" not in df.columns:
        continue
    last100 = df.tail(100)
    label   = os.path.basename(os.path.dirname(path)).replace("_"," ")
    records.append({
        "Method":       label,
        "MeanFidelity": last100.Fidelity.mean(),
        "StdFidelity":  last100.Fidelity.std(),
        "MeanReward":   last100.Reward.mean(),
        "StdReward":    last100.Reward.std()
    })

summary = pd.DataFrame(records).sort_values("MeanFidelity", ascending=False)
os.makedirs("results/processed", exist_ok=True)
summary.to_csv("results/processed/summary_table.csv", index=False)

# Print a plain-text table
print("\nSummary of last 100 steps (mean ± std):\n")
print(summary.to_string(index=False))
