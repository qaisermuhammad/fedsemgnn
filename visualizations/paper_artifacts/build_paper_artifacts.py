import os
import glob
import math
import textwrap
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Config
# ----------------------------
RESULTS_ROOT = "results"
PLOTS_DIR = Path(RESULTS_ROOT) / "plots_compare"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

LAST_K = 100          # window for the “paper” summary
ROLL = 25             # smoothing for time-series overlays (min-max normalized)

# Known column names we expect (your logging matches this now)
REQ_COLS = ["Step", "Reward", "Latency_ms", "Fidelity_pct"]
# optional columns (only used if present)
OPT_COLS = ["Bytes_step_MB", "Bytes_cum_MB", "Power_W", "Migrations"]

# ----------------------------
# Helpers
# ----------------------------
def discover_metric_csvs(root=RESULTS_ROOT):
    # grab anything that looks like a run metrics CSV
    candidates = glob.glob(os.path.join(root, "**", "*metrics.csv"), recursive=True)
    # filter out duplicates like substep csv etc.
    # keep classical ones e.g. fedsemgnn_metrics.csv, flat_fedppo_metrics.csv, ...
    return [p for p in candidates if os.path.isfile(p)]

def strategy_name_from_path(p):
    name = os.path.basename(p)
    # heuristics for a nice label
    if "fedsemgnn" in name.lower():
        return "FedSemGNN"
    if "flat" in name.lower() and "ppo" in name.lower():
        return "FlatFedPPO"
    if "hier" in name.lower() and "ppo" in name.lower():
        return "HierFedPPO"
    if "hsqf" in name.lower():
        return "HSQF"
    if "random" in name.lower():
        return "Random"
    # fallback: take folder name
    return Path(p).parent.name

def load_and_check(path):
    df = pd.read_csv(path)
    missing = [c for c in REQ_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")
    return df

def last_k(df, k=LAST_K):
    if len(df) < k:
        k = len(df)
    return df.tail(k).copy(), k

def minmax_norm(series):
    s = pd.Series(series).astype(float)
    if len(s) == 0 or np.all(np.isnan(s)):
        return pd.Series(np.zeros_like(s, dtype=float)), True  # flat series
    lo, hi = float(np.nanmin(s)), float(np.nanmax(s))
    if math.isclose(hi, lo):
        return pd.Series(np.zeros_like(s, dtype=float)), True  # flat series
    return (s - lo) / (hi - lo), False

def save_bar(values_dict, title, ylabel, fname):
    labels = list(values_dict.keys())
    vals = [values_dict[k] for k in labels]
    plt.figure(figsize=(7, 4))
    plt.bar(labels, vals)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=15)
    plt.tight_layout()
    out = PLOTS_DIR / fname
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"[ok] saved: {out}")

def save_overlay_time_series(data_dict, metric_key, title, fname, roll=ROLL):
    plt.figure(figsize=(7.5, 4.2))
    flat_flags = []
    for name, df in data_dict.items():
        # smooth a bit to make lines readable
        s = df[metric_key].rolling(roll, min_periods=1).mean()
        y, flat = minmax_norm(s)
        flat_flags.append(flat)
        plt.plot(df["Step"], y, label=name, linewidth=1.8)
    plt.title(title + " (min–max normalized)")
    plt.xlabel("Step")
    plt.ylabel("Normalized value")
    plt.legend(ncol=2)
    plt.tight_layout()
    out = PLOTS_DIR / fname
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"[ok] saved: {out}")
    if all(flat_flags):
        print(f"[note] All series for '{metric_key}' were flat (constant). A flat line is expected in that case.")

# ----------------------------
# Main
# ----------------------------
def main():
    csvs = discover_metric_csvs(RESULTS_ROOT)
    if not csvs:
        print("[warn] No metrics CSVs found.")
        return

    # Load all, check schema, bucket by strategy
    runs = {}
    for p in csvs:
        try:
            df = load_and_check(p)
        except Exception as e:
            print(f"[skip] {p}: {e}")
            continue
        strat = strategy_name_from_path(p)
        runs[strat] = {"path": p, "df": df}

    if not runs:
        print("[warn] No valid runs with required columns.")
        return

    # Build last-K summary
    summary_rows = []
    for strat, obj in runs.items():
        df = obj["df"].sort_values("Step")
        tail, used = last_k(df, LAST_K)

        rec = {
            "strategy": strat,
            "reward_mean_last100": float(tail["Reward"].mean()),
            "latency_ms_mean_last100": float(tail["Latency_ms"].mean()),
            "fidelity_pct_mean_last100": float(tail["Fidelity_pct"].mean()),
            "bytes_mb_mean_last100": float(tail["Bytes_step_MB"].mean()) if "Bytes_step_MB" in tail.columns else np.nan,
            "power_w_mean_last100": float(tail["Power_W"].mean()) if "Power_W" in tail.columns else np.nan,
            "steps_used": used
        }
        summary_rows.append(rec)

    summary_df = pd.DataFrame(summary_rows).sort_values("strategy")
    out_csv = PLOTS_DIR / "compare_summary_last100.csv"
    summary_df.to_csv(out_csv, index=False)
    print(summary_df.to_string(index=False))
    print(f"[ok] saved: {out_csv}")

    # Bar charts (last 100)
    save_bar({r["strategy"]: r["reward_mean_last100"] for _, r in summary_df.iterrows()},
             f"Reward (mean of last {LAST_K} steps)", "Reward (a.u.)", "compare_reward.png")

    save_bar({r["strategy"]: r["latency_ms_mean_last100"] for _, r in summary_df.iterrows()},
             f"Latency (mean of last {LAST_K} steps)", "Latency (ms)", "compare_latency.png")

    save_bar({r["strategy"]: r["fidelity_pct_mean_last100"] for _, r in summary_df.iterrows()},
             f"Fidelity (mean of last {LAST_K} steps)", "Fidelity (%)", "compare_fidelity.png")

    # Time-series overlays (min–max normalized)
    # Only include strategies that have enough rows
    ts_data = {name: runs[name]["df"].sort_values("Step") for name in runs.keys()}
    save_overlay_time_series(ts_data, "Reward", "Reward over time", "normalized_reward_minmax.png")
    save_overlay_time_series(ts_data, "Latency_ms", "Latency over time", "normalized_latency_minmax.png")
    save_overlay_time_series(ts_data, "Fidelity_pct", "Fidelity over time", "normalized_fidelity_minmax.png")

    # LaTeX table for the paper (based on last 100)
    # If you want the exact values from your earlier paper table, adjust here.

    latex = textwrap.dedent(f"""
        % Auto-generated by build_paper_artifacts.py
        \\begin{{table*}}[t]
        \\caption{{Summary over last {LAST_K} steps. Latency is per orchestration epoch; Fidelity is system-wide average.}}
        \\label{{tab:compare_last100}}
        \\centering
        \\begin{{tabular}}{{lcccc}}
            \\toprule
            \\textbf{{Strategy}} & \\textbf{{Reward (mean)}} & \\textbf{{Latency (ms)}} & \\textbf{{Fidelity (\\%)}} & \\textbf{{Bytes/step (MB) [opt]}} \\\\
            \\midrule
    """).strip("\n")



    for _, r in summary_df.iterrows():
        bytes_str = ("{:.3f}".format(r["bytes_mb_mean_last100"])) if not np.isnan(r["bytes_mb_mean_last100"]) else "--"
        latex += f"\n        {r['strategy']} & {r['reward_mean_last100']:.2f} & {r['latency_ms_mean_last100']:.3f} & {r['fidelity_pct_mean_last100']:.1f} & {bytes_str} \\\\"

    latex += textwrap.dedent("""
        \\bottomrule
      \\end{tabular}
    \\end{table*}
    """)
    out_tex = PLOTS_DIR / "summary_table.tex"
    with open(out_tex, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"[ok] saved: {out_tex}")
    print("\nPaste the LaTeX table from:", out_tex)

if __name__ == "__main__":
    main()
