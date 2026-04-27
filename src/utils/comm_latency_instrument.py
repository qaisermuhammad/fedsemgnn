import time, csv, os, functools
from threading import RLock

# CONFIG
OUT_DIR     = "results/processed"
LOG_CSV     = os.path.join(OUT_DIR, "comm_latency.csv")
os.makedirs(OUT_DIR, exist_ok=True)
_lock = RLock()

# initialize log header once
if not os.path.exists(LOG_CSV):
    with open(LOG_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Step", "CallName", "StartTs", "EndTs", "Duration_ms"])

def log_comm_latency(step_getter):
    """
    Decorator to wrap any comms function.
    step_getter: a callable returning the current simulation step (int).
    """
    def deco(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            step = step_getter()
            start = time.time()
            result = fn(*args, **kwargs)
            end   = time.time()
            dur   = (end - start)*1000
            with _lock, open(LOG_CSV, "a", newline="") as f:
                csv.writer(f).writerow([step, fn.__name__, start, end, round(dur,3)])
            return result
        return wrapped
    return deco
