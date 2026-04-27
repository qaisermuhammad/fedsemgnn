# step_latency_instrument.py
#!/usr/bin/env python3

import time
import csv
import os
import functools

OUT_DIR = "results/processed"
LOG_CSV = os.path.join(OUT_DIR, "step_latency.csv")
os.makedirs(OUT_DIR, exist_ok=True)

# write header if missing
if not os.path.exists(LOG_CSV):
    with open(LOG_CSV, "w", newline="") as f:
        csv.writer(f).writerow(["Step", "Duration_ms"])

def log_step_latency(fn):
    """Decorator: wraps fedsemgnn_algorithm to log its execution time."""
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        # derive step from metrics_history length with fallback imports
        try:
            from src.core.FedSemGNN import metrics_history
        except ImportError:
            metrics_history = []
        
        step = len(metrics_history) + 1

        start = time.time()
        result = fn(*args, **kwargs)
        end   = time.time()

        dur_ms = (end - start) * 1000
        with open(LOG_CSV, "a", newline="") as f:
            csv.writer(f).writerow([step, round(dur_ms, 3)])
        return result
    return wrapped
