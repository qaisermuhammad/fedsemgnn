#plot_comparison.py


import glob, os
import pandas as pd
import matplotlib.pyplot as plt

OUT = "results/processed/all_fidelity.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
plt.figure(figsize=(10,6))

for path in glob.glob("results/*_*_*steps/fedsemgnn_metrics.csv"):
    df = pd.read_csv(path)
    if "Fidelity" not in df.columns: 
        continue

    label = os.path.basename(os.path.dirname(path)).replace("_"," ")
    # plot noisy raw curve
    plt.plot(df.Step, df.Fidelity, color="lightgray", alpha=0.3)
    # plot 10‐step moving average
    df["MA10"] = df.Fidelity.rolling(10, min_periods=1).mean()
    plt.plot(df.Step, df.MA10, linewidth=1.5, label=label)

plt.xlabel("Step")
plt.ylabel("Semantic Fidelity")
plt.title("Method Comparison (10‐step MA)")
plt.legend(fontsize=8, ncol=2)
plt.grid(alpha=0.2)
plt.tight_layout()
plt.savefig(OUT, dpi=500)
plt.show()
