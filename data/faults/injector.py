import random

def dual_cluster_outage(n_clusters, p=0.02, dur_s=30):
    if random.random() < p:
        a = random.randrange(n_clusters)
        b = (a + random.randrange(1, n_clusters)) % n_clusters
        return {a: dur_s, b: dur_s}
    return {}
