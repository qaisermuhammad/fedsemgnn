import random

def sample_staleness(bytes_tx, link_mbps, compute_ms):
    net_ms = (bytes_tx*8) / (link_mbps*1e6) * 1e3
    jitter = random.lognormvariate(-6, 1)
    return max(0.0, net_ms + compute_ms + jitter)
