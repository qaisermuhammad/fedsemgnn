# metrics_loader.py
import pandas as pd

#REQUIRED = ["Step","Power","Reward","Latency","Fidelity","BytesExchanged"]
#If it is raising an error, uncommend the above REQUIRED variable and comment below.
REQUIRED = ["Step","Power_W","Reward","Latency_ms","Fidelity_pct","Bytes_cum_MB"]


def load_metrics(path):
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing columns: {missing}")
    return df

def aggregate_for_bars(df):
    # Fidelity: if 0..1 convert to %
    fid = df["Fidelity"].mean()
    if fid <= 1.0:
        fid *= 100.0

    # BytesExchanged is cumulative in your runs → take max and convert to MB
    total_mb = df["BytesExchanged"].astype(float).max() / 1e6

    return {
        "reward":   float(df["Reward"].mean()),
        "latency":  float(df["Latency"].mean()),   # already seconds
        "fidelity": float(fid),
        "bytes_mb": float(total_mb),
        "power":    float(df["Power"].mean()),
    }
