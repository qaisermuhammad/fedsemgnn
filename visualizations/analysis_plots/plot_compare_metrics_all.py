# plot_compare_metrics_all.py (improved)
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional, Tuple

# ========= EDIT THESE: point to your metric CSVs =========
STRATEGY_CSVS: Dict[str, str] = {
    "FedSemGNN": r"results/fedsemgnn_metrics.csv",
    "FlatFedPPO": r"results/flat_fedppo_metrics.csv",
    "HierFedPPO": r"results/hier_fedppo_metrics.csv",
    "HSQF":       r"results/hsqf_metrics.csv",
    "Random":     r"results/random_place_metrics.csv",
}
# If your per-step/cumulative bytes live in a *different* CSV, set it here.
# Leave a value out to fall back to STRATEGY_CSVS[strategy].
BYTES_CSVS: Dict[str, str] = {
    # "FedSemGNN": r"results/run_default/fedsemgnn_comm.csv",
    # "FlatFedPPO": r"...",
}
# =========================================================

OUTDIR = "results/plots_compare"
os.makedirs(OUTDIR, exist_ok=True)
SMOOTH_WINDOW = 5  # set 0 to disable

def _read_csv(path: str) -> Optional[pd.DataFrame]:
    if not os.path.exists(path):
        print(f"[warn] missing: {path}")
        return None
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print(f"[warn] failed to read {path}: {e}")
        return None

def _get_col(df: pd.DataFrame, candidates) -> Optional[str]:
    lower = {c.lower(): c for c in df.columns}
    for nm in candidates:
        if nm.lower() in lower:
            return lower[nm.lower()]
    return None

def _ensure_step(df: pd.DataFrame) -> pd.DataFrame:
    step_col = _get_col(df, ["step", "t", "epoch", "iter"])
    if step_col is None:
        df = df.copy()
        df["step"] = np.arange(len(df))
    elif step_col != "step":
        df = df.rename(columns={step_col: "step"})
    return df

def _smooth(s: pd.Series) -> pd.Series:
    if SMOOTH_WINDOW and SMOOTH_WINDOW > 1:
        return s.rolling(SMOOTH_WINDOW, min_periods=1).mean()
    return s

def _latency_ms(df: pd.DataFrame) -> Optional[pd.Series]:
    # Prefer explicit ms; else detect seconds and convert
    c_ms = _get_col(df, ["latency_ms", "lat_ms"])
    if c_ms:
        return df[c_ms].astype(float)
    c_s = _get_col(df, ["latency_s", "lat_s"])
    if c_s:
        return df[c_s].astype(float) * 1000.0
    c_generic = _get_col(df, ["latency"])
    if c_generic:
        # Heuristic: if max<10, probably seconds -> ms
        s = df[c_generic].astype(float)
        return s * 1000.0 if s.max() < 10 else s
    return None

def _fidelity_pct(df: pd.DataFrame) -> Optional[pd.Series]:
    c = _get_col(df, ["fidelity_pct", "fidelity"])
    if not c:
        return None
    s = df[c].astype(float)
    if s.max() <= 1.001:  # 0..1 -> %
        s = s * 100.0
    return s

def _reward(df: pd.DataFrame) -> Optional[pd.Series]:
    c = _get_col(df, ["reward", "reward_per_step", "avg_reward"])
    return df[c].astype(float) if c else None

def _bytes_mb_from_df(df: pd.DataFrame) -> Tuple[Optional[pd.Series], Optional[pd.Series]]:
    """Return (per_step_MB, cumulative_MB) if present/derivable."""
    # 1) direct per-step MB
    c_step_mb = _get_col(df, ["bytes_mb", "per_step_bytes_mb", "comm_mb"])
    if c_step_mb:
        per_step = df[c_step_mb].astype(float)
        cum = per_step.cumsum()
        return per_step, cum

    # 2) per-step raw bytes
    c_step_bytes = _get_col(df, ["bytes", "per_step_bytes", "comm_bytes"])
    if c_step_bytes:
        per_step = df[c_step_bytes].astype(float) / (1024 * 1024.0)
        cum = per_step.cumsum()
        return per_step, cum

    # 3) cumulative MB present
    c_cum_mb = _get_col(df, ["cumulative_bytes_mb", "cum_bytes_mb", "bytes_cum_mb"])
    if c_cum_mb:
        cum = df[c_cum_mb].astype(float)
        per_step = cum.diff().fillna(cum.iloc[0])
        return per_step, cum

    # 4) cumulative raw bytes present
    c_cum_bytes = _get_col(df, ["cumulative_bytes", "cum_bytes", "bytes_cum"])
    if c_cum_bytes:
        cum = df[c_cum_bytes].astype(float) / (1024 * 1024.0)
        per_step = cum.diff().fillna(cum.iloc[0])
        return per_step, cum

    return None, None

def _get_bytes_frames(strategy: str) -> Optional[pd.DataFrame]:
    # Prefer a dedicated bytes CSV if provided, else fall back to main CSV
    path = BYTES_CSVS.get(strategy, STRATEGY_CSVS.get(strategy))
    if not path:
        return None
    df = _read_csv(path)
    if df is None:
        return None
    return _ensure_step(df)

def _plot_compare(series_map: Dict[str, Tuple[pd.Series, pd.Series]],
                  title: str, ylabel: str, outfile: str, plot_cumulative=False):
    if not series_map:
        print(f"[info] No data available to plot: {title}")
        return
    plt.figure(figsize=(8, 4.6))
    for name, (x, y) in series_map.items():
        if y is None or x is None:
            continue
        plt.plot(x, _smooth(y), label=name)
    plt.title(title)
    plt.xlabel("Step")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.25)
    plt.legend()
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, outfile)
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"[ok] saved: {out}")

def main():
    # Load primary CSVs
    loaded = {name: _read_csv(path) for name, path in STRATEGY_CSVS.items()}
    loaded = {k: _ensure_step(v) for k, v in loaded.items() if v is not None}

    # Reward
    reward_series = {}
    for name, df in loaded.items():
        r = _reward(df)
        if r is not None:
            reward_series[name] = (df["step"], r)
        else:
            print(f"[info] {name}: reward column not found.")
    _plot_compare(reward_series, "Reward per Step (All Strategies)", "Reward/step", "compare_reward.png")

    # Latency (ms)
    lat_series = {}
    for name, df in loaded.items():
        s = _latency_ms(df)
        if s is not None:
            lat_series[name] = (df["step"], s)
        else:
            print(f"[info] {name}: latency column not found.")
    _plot_compare(lat_series, "Latency (All Strategies)", "Latency (ms)", "compare_latency.png")

    # Fidelity (%)
    fid_series = {}
    for name, df in loaded.items():
        s = _fidelity_pct(df)
        if s is not None:
            fid_series[name] = (df["step"], s)
        else:
            print(f"[info] {name}: fidelity column not found.")
    _plot_compare(fid_series, "Fidelity (All Strategies)", "Fidelity (%)", "compare_fidelity.png")

    # Bytes (per-step MB) and cumulative MB
    bytes_step_map, bytes_cum_map = {}, {}
    for name in STRATEGY_CSVS.keys():
        df_b = _get_bytes_frames(name)
        if df_b is None:
            print(f"[info] {name}: no bytes CSV found.")
            continue
        per_step_mb, cum_mb = _bytes_mb_from_df(df_b)
        if per_step_mb is not None:
            bytes_step_map[name] = (df_b["step"], per_step_mb)
        if cum_mb is not None:
            bytes_cum_map[name] = (df_b["step"], cum_mb)
        if per_step_mb is None and cum_mb is None:
            print(f"[info] {name}: no bytes columns detected in {BYTES_CSVS.get(name, STRATEGY_CSVS.get(name))}.")

    _plot_compare(bytes_step_map, "Per-step Bytes Exchanged (All Strategies)", "MB", "compare_bytes_step.png")
    _plot_compare(bytes_cum_map, "Cumulative Bytes Exchanged (All Strategies)", "MB (cumulative)", "compare_bytes_cumulative.png")

    # Summary (last 100 steps)
    rows = []
    for name, df in loaded.items():
        tail = df.tail(100)
        r = _reward(df)
        r_mean = tail[_get_col(df, ["reward", "reward_per_step", "avg_reward"])] .mean() if _get_col(df, ["reward", "reward_per_step", "avg_reward"]) else np.nan
        l = _latency_ms(df); l_mean = l.tail(100).mean() if l is not None else np.nan
        f = _fidelity_pct(df); f_mean = f.tail(100).mean() if f is not None else np.nan

        # bytes from bytes source
        df_b = _get_bytes_frames(name)
        if df_b is not None:
            per_step_mb, cum_mb = _bytes_mb_from_df(df_b)
            b_mean = per_step_mb.tail(100).mean() if per_step_mb is not None else np.nan
        else:
            b_mean = np.nan

        rows.append(dict(strategy=name,
                         reward_mean_last100=r_mean,
                         latency_ms_mean_last100=l_mean,
                         fidelity_pct_mean_last100=f_mean,
                         bytes_mb_mean_last100=b_mean))
    summ = pd.DataFrame(rows).sort_values("strategy")
    os.makedirs(OUTDIR, exist_ok=True)
    summ.to_csv(os.path.join(OUTDIR, "compare_summary_last100.csv"), index=False)
    print(summ.to_string(index=False))

if __name__ == "__main__":
    main()
