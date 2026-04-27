import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import pandas as pd


def _run_one(script: Path, steps: int, override_num_nodes: Optional[int], config: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    config_path = out_dir / "config_override.json"
    config_path.write_text(json.dumps(config, indent=2))

    metrics_src = Path("results") / "fedsemgnn_metrics.csv"
    if metrics_src.exists():
        metrics_src.unlink()

    cmd = [
        sys.executable,
        str(script),
        "--steps",
        str(steps),
        "--config-override",
        str(config_path),
    ]
    if override_num_nodes is not None:
        cmd += ["--override-num-nodes", str(override_num_nodes)]

    print("[sensitivity] Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=Path(__file__).resolve().parents[1])
    if result.returncode != 0:
        raise RuntimeError(f"Run failed with return code {result.returncode}")

    if not metrics_src.exists():
        raise FileNotFoundError(f"Expected metrics file not found: {metrics_src}")

    metrics_dst = out_dir / "fedsemgnn_metrics.csv"
    metrics_dst.write_bytes(metrics_src.read_bytes())
    return metrics_dst


def _run_one_trial(
    script: Path,
    steps: int,
    override_num_nodes: Optional[int],
    config: dict,
    out_dir: Path,
    seed: int,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    config_path = out_dir / "config_override.json"
    config_path.write_text(json.dumps(config, indent=2))

    metrics_src = Path("results") / "fedsemgnn_metrics.csv"
    if metrics_src.exists():
        metrics_src.unlink()

    cmd = [
        sys.executable,
        str(script),
        "--steps",
        str(steps),
        "--seed",
        str(seed),
        "--config-override",
        str(config_path),
    ]
    if override_num_nodes is not None:
        cmd += ["--override-num-nodes", str(override_num_nodes)]

    print("[sensitivity] Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=Path(__file__).resolve().parents[1])
    if result.returncode != 0:
        raise RuntimeError(f"Run failed with return code {result.returncode}")

    if not metrics_src.exists():
        raise FileNotFoundError(f"Expected metrics file not found: {metrics_src}")

    metrics_dst = out_dir / "fedsemgnn_metrics.csv"
    metrics_dst.write_bytes(metrics_src.read_bytes())
    return metrics_dst


def main():
    parser = argparse.ArgumentParser(description="Run FedSemGNN parameter sensitivity sweeps")
    parser.add_argument("--steps", type=int, default=200, help="Steps per run")
    parser.add_argument("--override-num-nodes", type=int, default=None)
    parser.add_argument("--tau", type=str, default="0.1,0.3,0.5,0.7", help="Comma-separated semantic thresholds (use 'none' to skip)")
    parser.add_argument("--ewc", type=str, default="0.0,0.1,0.4,1.0", help="Comma-separated EWC lambdas (use 'none' to skip)")
    parser.add_argument("--sem-dim", type=str, default="", help="Comma-separated semantic dimensions (e.g. 8,16,32)")
    parser.add_argument("--sync-interval", type=str, default="", help="Comma-separated intra-sync intervals K1 (e.g. 5,10,20)")
    parser.add_argument("--buffer", type=str, default="", help="Comma-separated replay-buffer capacities (e.g. 10000,20000,40000)")
    parser.add_argument("--trials", type=int, default=1, help="Independent trials per setting")
    parser.add_argument("--seed-base", type=int, default=1000, help="Base seed; trial seeds are seed_base+trial")
    parser.add_argument("--out", type=str, default="results/sensitivity", help="Output directory")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    fedsem_script = repo_root / "src" / "algorithms" / "FedSemGNN.py"

    tau_values = [float(x.strip()) for x in args.tau.split(",") if x.strip() and x.strip().lower() != "none"]
    ewc_values = [float(x.strip()) for x in args.ewc.split(",") if x.strip() and x.strip().lower() != "none"]
    sem_dim_values = [int(x.strip()) for x in args.sem_dim.split(",") if x.strip()]
    sync_values = [int(x.strip()) for x in args.sync_interval.split(",") if x.strip()]
    buffer_values = [int(x.strip()) for x in args.buffer.split(",") if x.strip()]

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    trial_rows: list[dict] = []

    def _row_from_metrics(df: pd.DataFrame) -> dict:
        svc_weighted = df.get("SvcLatency_weighted_ms", pd.Series([float("nan")]))
        return {
            "reward_mean": float(df["Reward"].mean()),
            "reward_last": float(df["Reward"].iloc[-1]),
            "fidelity_mean": float(df["Fidelity_pct"].mean()),
            "fidelity_last": float(df["Fidelity_pct"].iloc[-1]),
            "latency_mean_ms": float(df["Latency_ms"].mean()),
            "svc_latency_weighted_mean_ms": float(svc_weighted.mean()),
        }

    for tau in tau_values:
        cfg = {
            "semantic_match_threshold": tau,
            "ewc_lambda": 0.4,
        }
        for trial in range(args.trials):
            seed = int(args.seed_base + trial)
            run_dir = out_root / f"tau_{tau:g}" / f"trial_{trial:02d}_seed_{seed}"
            metrics_path = _run_one_trial(fedsem_script, args.steps, args.override_num_nodes, cfg, run_dir, seed)
            df = pd.read_csv(metrics_path)
            trial_rows.append({
                "sweep": "tau",
                "tau": tau,
                "ewc_lambda": 0.4,
                "trial": trial,
                "seed": seed,
                **_row_from_metrics(df),
            })

    for lam in ewc_values:
        cfg = {
            "semantic_match_threshold": 0.3,
            "ewc_lambda": lam,
        }
        for trial in range(args.trials):
            seed = int(args.seed_base + trial)
            run_dir = out_root / f"ewc_{lam:g}" / f"trial_{trial:02d}_seed_{seed}"
            metrics_path = _run_one_trial(fedsem_script, args.steps, args.override_num_nodes, cfg, run_dir, seed)
            df = pd.read_csv(metrics_path)
            trial_rows.append({
                "sweep": "ewc",
                "tau": 0.3,
                "ewc_lambda": lam,
                "trial": trial,
                "seed": seed,
                **_row_from_metrics(df),
            })

    # --- Reviewer 2 sweeps: semantic_dim, sync_interval (K1), buffer_capacity ---

    for dim in sem_dim_values:
        cfg = {
            "semantic_match_threshold": 0.3,
            "ewc_lambda": 0.4,
            "semantic_dim": dim,
        }
        for trial in range(args.trials):
            seed = int(args.seed_base + trial)
            run_dir = out_root / f"semdim_{dim}" / f"trial_{trial:02d}_seed_{seed}"
            metrics_path = _run_one_trial(fedsem_script, args.steps, args.override_num_nodes, cfg, run_dir, seed)
            df = pd.read_csv(metrics_path)
            trial_rows.append({
                "sweep": "sem_dim",
                "tau": 0.3,
                "ewc_lambda": 0.4,
                "sem_dim": dim,
                "sync_interval": 10,
                "buffer_capacity": 20000,
                "trial": trial,
                "seed": seed,
                **_row_from_metrics(df),
            })

    for sync in sync_values:
        cfg = {
            "semantic_match_threshold": 0.3,
            "ewc_lambda": 0.4,
            "sync_interval": sync,
        }
        for trial in range(args.trials):
            seed = int(args.seed_base + trial)
            run_dir = out_root / f"sync_{sync}" / f"trial_{trial:02d}_seed_{seed}"
            metrics_path = _run_one_trial(fedsem_script, args.steps, args.override_num_nodes, cfg, run_dir, seed)
            df = pd.read_csv(metrics_path)
            trial_rows.append({
                "sweep": "sync_interval",
                "tau": 0.3,
                "ewc_lambda": 0.4,
                "sem_dim": 16,
                "sync_interval": sync,
                "buffer_capacity": 20000,
                "trial": trial,
                "seed": seed,
                **_row_from_metrics(df),
            })

    for buf in buffer_values:
        cfg = {
            "semantic_match_threshold": 0.3,
            "ewc_lambda": 0.4,
            "buffer_capacity": buf,
        }
        for trial in range(args.trials):
            seed = int(args.seed_base + trial)
            run_dir = out_root / f"buffer_{buf}" / f"trial_{trial:02d}_seed_{seed}"
            metrics_path = _run_one_trial(fedsem_script, args.steps, args.override_num_nodes, cfg, run_dir, seed)
            df = pd.read_csv(metrics_path)
            trial_rows.append({
                "sweep": "buffer",
                "tau": 0.3,
                "ewc_lambda": 0.4,
                "sem_dim": 16,
                "sync_interval": 10,
                "buffer_capacity": buf,
                "trial": trial,
                "seed": seed,
                **_row_from_metrics(df),
            })

    trials_df = pd.DataFrame(trial_rows)
    # Fill missing columns for legacy tau/ewc rows
    for col in ["sem_dim", "sync_interval", "buffer_capacity"]:
        if col not in trials_df.columns:
            trials_df[col] = pd.NA
        else:
            trials_df[col] = trials_df[col].fillna(pd.NA)
    trials_path = out_root / "summary_trials.csv"
    trials_df.to_csv(trials_path, index=False)

    group_cols = ["sweep", "tau", "ewc_lambda", "sem_dim", "sync_interval", "buffer_capacity"]
    # Only include groupby columns that exist in the dataframe
    group_cols = [c for c in group_cols if c in trials_df.columns]

    summary = (
        trials_df
        .groupby(group_cols, as_index=False, dropna=False)
        .agg(
            reward_mean_mean=("reward_mean", "mean"),
            reward_mean_std=("reward_mean", "std"),
            reward_last_mean=("reward_last", "mean"),
            reward_last_std=("reward_last", "std"),
            fidelity_mean_mean=("fidelity_mean", "mean"),
            fidelity_mean_std=("fidelity_mean", "std"),
            fidelity_last_mean=("fidelity_last", "mean"),
            fidelity_last_std=("fidelity_last", "std"),
            latency_mean_ms_mean=("latency_mean_ms", "mean"),
            latency_mean_ms_std=("latency_mean_ms", "std"),
            svc_latency_weighted_mean_ms_mean=("svc_latency_weighted_mean_ms", "mean"),
            svc_latency_weighted_mean_ms_std=("svc_latency_weighted_mean_ms", "std"),
        )
    )

    summary_path = out_root / "summary.csv"
    summary.to_csv(summary_path, index=False)
    print("[sensitivity] Wrote", summary_path)
    print("[sensitivity] Wrote", trials_path)


if __name__ == "__main__":
    main()
