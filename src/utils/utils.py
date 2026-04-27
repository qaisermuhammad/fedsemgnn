# utils.py
import os

import pandas as pd


def save_metrics_csv(
    prefix,
    rewards,
    latencies_ms,
    fidelities_pct,
    powers_w,
    migrations,
    bytes_step=None,
    bytes_cum=None,
    num_nodes=None,
    user_coords=None,
    edge_coords=None,
    extra_columns=None,
):
    """
    Save metrics to CSV in the unified schema.

    Parameters:
        prefix (str): File prefix for saving.
        rewards (list[float]): Reward values per step.
        latencies_ms (list[float]): Latency values in milliseconds.
        fidelities_pct (list[float]): Fidelity values in percentage (0-100).
        powers_w (list[float]): Power consumption in Watts.
        migrations (list[int]): Migration counts.
        bytes_step (list[float] or None): Per-step bytes in MB (optional).
        bytes_cum (list[float] or None): Cumulative bytes in MB (optional).
        num_nodes (int or None): Number of nodes used in the experiment (optional, default None).
    """
    import inspect
    os.makedirs("results", exist_ok=True)
    n = len(rewards)

    if user_coords is None:
        user_coords = [None] * n
    if edge_coords is None:
        edge_coords = [None] * n

    # Ensure optional lists are filled with None if not provided
    if bytes_step is None:
        bytes_step = [None] * n
    if bytes_cum is None:
        bytes_cum = [None] * n

    # Try to get num_nodes from caller if not provided
    frame = inspect.currentframe()
    try:
        outer = frame.f_back
        if num_nodes is None:
            if 'num_nodes' in outer.f_locals:
                num_nodes = outer.f_locals['num_nodes']
            elif 'max_nodes' in outer.f_locals:
                num_nodes = outer.f_locals['max_nodes']
    finally:
        del frame

    if num_nodes is None:
        # fallback: try config import
        try:
            from src.core.config import SIMULATION_CONFIG
            num_nodes = SIMULATION_CONFIG.get("max_nodes", None)
        except Exception:
            num_nodes = None

    df = pd.DataFrame({
        "Step":          range(1, n + 1),
        "Reward":        rewards,
        "Latency_ms":    latencies_ms,
        "Fidelity_pct":  fidelities_pct,
        "Power_W":       powers_w,
        "Migrations":    migrations,
        "Bytes_step_MB": bytes_step,
        "Bytes_cum_MB":  bytes_cum,
        "Num_Nodes":     [num_nodes] * n if num_nodes is not None else [None] * n,
        "User_Coords":   user_coords,
        "EdgeServer_Coords": edge_coords
    })

    if extra_columns:
        for k, v in extra_columns.items():
            if v is None:
                continue
            if len(v) != n:
                raise ValueError(f"extra_columns[{k!r}] length {len(v)} != n {n}")
            df[k] = v
    filename = f"results/{prefix}_metrics.csv"
    df.to_csv(filename, index=False)
    # Avoid console encoding issues on Windows shells (no emojis)
    try:
        print(f"Saved metrics to {filename} (schema aligned)")
    except Exception:
        # Fallback plain print
        print("Saved metrics:", filename)
