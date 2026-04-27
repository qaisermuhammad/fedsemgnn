import numpy as np

def top_k_params(params, k_ratio=0.1):
    k = max(1, int(len(params) * k_ratio))
    idx = np.argpartition(np.abs(params), -k)[-k:]
    mask = np.zeros_like(params, dtype=bool)
    mask[idx] = True
    return params * mask
