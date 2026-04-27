import numpy as np

def is_novel(x, memory, delta=0.35):
    sims = [np.dot(x,m)/ (np.linalg.norm(x)*np.linalg.norm(m)+1e-9) for m in memory]
    return (len(sims)==0) or (max(sims) < 1-delta)
