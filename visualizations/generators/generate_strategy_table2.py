# generate_strategy_table2.py
from pathlib import Path
import re
import pandas as pd
import numpy as np

# ------------------- CONFIG -------------------
RESULTS_DIR = Path("results")

# If you want per-node power, set your node count here (e.g., 50). Leave 0 for system total.
NODES = 0

# Scale reward values for readability in the paper (e.g., 7700 -> 7.70)
REWARD_SCALE = 1000.0  # set to 1.0 to disable scaling

# The strategies we want to report and their folder aliases (in print order)
TARGETS = ["FedSemGNN", "FlatFedPPO", "HierFedPPO", "HSQF Heur.", "Random"]
ALIAS_MAP = {
    r"^FedSemGNN": "FedSemGNN",
    r"^FlatFedPPO": "FlatFedPPO",
    r"^HierFedPPO": "HierFedPPO",
    r"^HSQF": "HSQF Heur.",
    r"^RandomPlacement|^Random$": "Random",
}

# Columns we expect (we’ll fill missing with NaN and handle gracefully)
REQUIRED = ["Step","Power","Reward","Latency","Fidelity","BytesExchanged"]


# ------------------- DISCOVERY -------------------
def normalize_strategy(folder_name: str):
    for pat, label in ALIAS_MAP.items():
        if re.search(pat, folder_name, re.IGNORECASE):
            return label
    return None

def score_folder(p: Path):
    """Prefer 1000steps > 500steps, GCN > linear, newer mtime."""
    name = p.name.lower()
    steps = 1000 if "1000" in name else (500 if "500" in name else 0)
    enc   = 1 if "gcn" in name else 0
    mtime = int(p.stat().st_mtime)
    return (steps, enc, mtime)

def discover_sources():
    """Pick the best run per strategy under results/ (by steps, encoder, mtime)."""
    sources = {}
    if not RESULTS_DIR.exists():
        return {}
    for run_dir in RESULTS_DIR.iterdir():
        if not run_dir.is_dir():
            continue
        csv = run_dir / "fedsemgnn_metrics.csv"
        if not csv.exists():
            continue
        label = normalize_strategy(run_dir.name)
        if not label:
            continue
        if label not in sources or score_folder(run_dir) > score_folder(sources[label].parent):
            sources[label] = csv
    return {k: sources[k] for k in TARGETS if k in sources}


# ------------------- HELPERS -------------------
def load_metrics(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Fill missing required columns with NaN and coerce numerics
    for c in REQUIRED:
        if c not in df.columns:
            df[c] = np.nan
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df.attrs["_run_dir"] = str(path.parent)
    return df

def pick_latency_ms(df: pd.DataFrame, run_dir: Path) -> float:
    """
    Return mean latency in ms.
    Try common column names (ms or s). Fallback to processed/substep_latency.csv if present.
    """
    candidates = [
        ("Latency_ms", 1.0), ("LatencyMS", 1.0), ("OrchLatencyMs", 1.0),
        ("avg_latency_ms", 1.0),
        ("Latency", 1000.0), ("avg_latency", 1000.0),  # seconds → ms
    ]
    for col, scale in candidates:
        if col in df.columns and df[col].notna().any():
            v = df[col].dropna().astype(float).mean() * scale
            if v > 0:
                return float(v)

    # Fallback to processed substep latency in this run's folder
    proc = Path(run_dir) / "processed" / "substep_latency.csv"
    if proc.exists():
        try:
            s = pd.read_csv(proc)
            for c in ["OrchLatency_ms", "Total_ms", "GCN_ms"]:
                if c in s.columns and pd.to_numeric(s[c], errors="coerce").notna().any():
                    mv = pd.to_numeric(s[c], errors="coerce").dropna().mean()
                    if mv > 0:
                        return float(mv)
        except Exception:
            pass

    return np.nan

def bytes_total_mb(df: pd.DataFrame) -> float:
    """Compute cumulative bytes delta (final - initial) in MB."""
    s = df["BytesExchanged"].dropna().astype(float)
    if len(s) >= 2:
        return float((s.iloc[-1] - s.iloc[0]) / 1e6)
    return np.nan

def power_w_mean(df: pd.DataFrame) -> float:
    """Mean power in W; convert from mW if it looks huge; optional per-node normalization."""
    p = df["Power"].dropna().astype(float)
    if not len(p):
        return np.nan
    p_mean = float(p.mean())
    if p_mean > 10000:  # likely mW → W
        p_mean /= 1000.0
    if NODES and NODES > 1:
        p_mean /= NODES
    return p_mean

# ---------- Reward aggregations ----------
def reward_series(df: pd.DataFrame) -> np.ndarray:
    return pd.to_numeric(df.get("Reward", pd.Series(dtype=float)), errors="coerce").dropna().values

def reward_per_step(df: pd.DataFrame) -> float:
    """
    Robust per-step reward:
    - If Reward is cumulative (mostly non-decreasing): mean of deltas.
    - Else (instantaneous): steady-state mean (last 30%).
    """
    r = reward_series(df)
    if r.size < 5:
        return float("nan")
    diffs = np.diff(r)
    nondec_ratio = (diffs >= -1e-9).mean()
    if nondec_ratio >= 0.9 and r[-1] > r[0]:
        return float(np.mean(diffs))  # cumulative → avg per-step increment
    # instantaneous → steady-state mean (last 30%)
    k = max(1, int(0.3 * r.size))
    return float(np.mean(r[-k:]))

def reward_total(df: pd.DataFrame) -> float:
    """
    Since Reward is per-step in your logs, define total as mean * number of steps.
    (Still useful for appendices; not shown in main table.)
    """
    r = reward_series(df)
    if r.size == 0:
        return float("nan")
    return float(np.mean(r) * r.size)

def reward_last30(df: pd.DataFrame) -> float:
    r = reward_series(df)
    if r.size == 0:
        return float("nan")
    k = max(1, int(0.3 * r.size))
    return float(np.mean(r[-k:]))

def fmt(val, unit=None, nd=2, na="N/A"):
    if val is None or (isinstance(val, float) and not np.isfinite(val)):
        return na
    if unit == "%":
        return f"{val:.1f}%"
    if isinstance(val, float):
        return f"{val:.{nd}f}"
    return str(val)


# ------------------- MAIN -------------------
def main():
    sources = discover_sources()
    if not sources:
        raise SystemExit("No fedsemgnn_metrics.csv found under results/")

    # First pass: compute per-strategy metrics
    rows = []
    step_map = {}
    for label, path in sources.items():
        df = load_metrics(path)
        run_dir = Path(df.attrs.get("_run_dir", "."))
        agg = {
            "reward_step": reward_per_step(df),
            "reward_tot": reward_total(df),
            "reward_last": reward_last30(df),
            "latency_ms": pick_latency_ms(df, run_dir),
            "fidelity": (
                df["Fidelity"].dropna().astype(float).mean()
                if df["Fidelity"].notna().any() else np.nan
            ),
            "bytes_mb": bytes_total_mb(df),
            "power_w": power_w_mean(df),
        }
        # convert fidelity to %
        if np.isfinite(agg["fidelity"]) and agg["fidelity"] <= 1.0:
            agg["fidelity"] *= 100.0

        rows.append((label, agg))
        step_map[label] = agg["reward_step"]

    # Compute baseline uplift vs Random (if Random present and finite)
    baseline = step_map.get("Random", np.nan)
    def uplift(val):
        if np.isfinite(val) and np.isfinite(baseline):
            return val - baseline
        return np.nan

    # --------- PAPER TABLE (7 columns) ----------
    paper_rows = []
    for label, agg in rows:
        paper_rows.append({
            "Strategy": label,
            "Reward/step": fmt(agg["reward_step"] / REWARD_SCALE, nd=2),
            "Uplift vs Random": fmt(uplift(agg["reward_step"]) / REWARD_SCALE, nd=2),
            "Latency (ms)": fmt(agg["latency_ms"], nd=3),
            "Fidelity": fmt(agg["fidelity"], unit="%", nd=1),
            "Bytes (MB)": fmt(agg["bytes_mb"], nd=1),
            "Power (W)": fmt(agg["power_w"], nd=1),
        })

    paper_table = pd.DataFrame(
        paper_rows,
        columns=["Strategy","Reward/step","Uplift vs Random","Latency (ms)","Fidelity","Bytes (MB)","Power (W)"]
    )
    paper_table.to_csv("summary_table_main.csv", index=False)
    print("\n=== Paper Table (copy into LaTeX) ===")
    print(paper_table.to_string(index=False))

    # --------- DIAGNOSTIC TABLE (appendix/debug) ----------
    diag_rows = []
    for label, agg in rows:
        diag_rows.append({
            "Strategy": label,
            "Reward/step (scaled)": fmt(agg["reward_step"] / REWARD_SCALE, nd=2),
            "Reward total (scaled)": fmt(agg["reward_tot"] / REWARD_SCALE, nd=1),
            "Reward (last30%) (scaled)": fmt(agg["reward_last"] / REWARD_SCALE, nd=2),
            "Latency (ms)": fmt(agg["latency_ms"], nd=3),
            "Fidelity": fmt(agg["fidelity"], unit="%", nd=1),
            "Bytes (MB)": fmt(agg["bytes_mb"], nd=1),
            "Power (W)": fmt(agg["power_w"], nd=1),
        })
    diag_table = pd.DataFrame(diag_rows)
    diag_table.to_csv("summary_table_diagnostics.csv", index=False)
    print("\n=== Diagnostics (saved to summary_table_diagnostics.csv) ===")
    print(diag_table.to_string(index=False))


if __name__ == "__main__":
    main()
