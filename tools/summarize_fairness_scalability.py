import os
import pandas as pd
import glob

RESULTS_DIR = "results/"

# List of algorithms and their metrics files
ALGO_FILES = [
    ("FedSemGNN", "FedSemGNN_metrics.csv"),
    ("FlatFedPPO", "flat_fedppo_metrics.csv"),
    ("HierFedPPO", "hier_fedppo_metrics.csv"),
    ("HSQF", "hsqf_metrics.csv"),
    ("RandomPlacement", "random_place_metrics.csv"),
]

def summarize_metrics(metrics_path):
    if not os.path.exists(metrics_path):
        return None
    df = pd.read_csv(metrics_path)
    summary = {
        "Num_Nodes": int(df["Num_Nodes"].iloc[0]) if "Num_Nodes" in df.columns else None,
        "Steps": len(df),
        "Reward_mean": df["Reward"].mean() if "Reward" in df.columns else None,
        "Latency_ms_mean": df["Latency_ms"].mean() if "Latency_ms" in df.columns else None,
        "Fidelity_pct_mean": df["Fidelity_pct"].mean() if "Fidelity_pct" in df.columns else None,
        "Power_W_mean": df["Power_W"].mean() if "Power_W" in df.columns else None,
        "Bytes_cum_MB": df["Bytes_cum_MB"].iloc[-1] if "Bytes_cum_MB" in df.columns else None,
    }
    return summary

def main():
    print("Algorithm,Num_Nodes,Steps,Reward_mean,Latency_ms_mean,Fidelity_pct_mean,Power_W_mean,Bytes_cum_MB")
    for algo, fname in ALGO_FILES:
        # Look for both default and tuning/100 nodes runs
        for path in glob.glob(os.path.join(RESULTS_DIR, f"**/{fname}"), recursive=True):
            summary = summarize_metrics(path)
            if summary:
                print(f"{algo},{summary['Num_Nodes']},{summary['Steps']},{summary['Reward_mean']:.2f},{summary['Latency_ms_mean']:.2f},{summary['Fidelity_pct_mean']:.2f},{summary['Power_W_mean']:.2f},{summary['Bytes_cum_MB']:.2f}")

if __name__ == "__main__":
    main()
