# metrics_logger.py
"""
Stub for metrics logger utilities used in cluster reward plotting.
"""
import json

def load_json_trace(path):
    """Load a JSON trace file and return its contents as a dict."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def extract_cluster_rewards(trace):
    """Extract cluster rewards from a trace dict. Assumes trace['clusters'] structure."""
    # Example: { 'clusters': { '0': [r1, r2, ...], '1': [r1, r2, ...], ... } }
    if 'clusters' in trace:
        return trace['clusters']
    return {}
