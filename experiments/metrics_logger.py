# metrics_logger.py
import numpy as np
import pandas as pd
import os
import json


def log_run_metrics(run_dir, run_id, metric_list):
    """
    Save a single run's metrics to disk.
    """
    df = pd.DataFrame(metric_list)
    path = os.path.join(run_dir, f"run_{run_id}.csv")
    df.to_csv(path, index=False)


def load_json_trace(trace_path):
    """Load simulation trace JSON"""
    with open(trace_path, "r") as f:
        return json.load(f)


def aggregate_runs(run_dir):
    """
    Aggregate all run CSVs in a directory.
    Returns: (mean_df, std_df)
    """
    all_dfs = []
    for file in os.listdir(run_dir):
        if file.endswith(".csv") and file.startswith("run_"):
            df = pd.read_csv(os.path.join(run_dir, file))
            all_dfs.append(df)

    stacked = np.stack([df["Reward"].values for df in all_dfs])
    mean_reward = np.mean(stacked, axis=0)
    std_reward = np.std(stacked, axis=0)

    return mean_reward, std_reward

def extract_cluster_rewards(trace_list):
    cluster_dict = {}
    for step in trace_list:
        system_metrics = step.get("SystemMetrics", {})
        rewards = system_metrics.get("ClusterRewards", [])
        for cid, reward in rewards:
            if cid not in cluster_dict:
                cluster_dict[cid] = []
            cluster_dict[cid].append(reward)
    return cluster_dict
