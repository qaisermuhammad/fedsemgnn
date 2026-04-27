# config.py

REWARD_SCALE = 1000.0  # divide per-step reward by this factor for display; set to 1.0 to disable

# Simulation parameters
SIMULATION_CONFIG = {
    "tick_duration":      1,               # seconds per step
    "simulation_input": "workloads/scale_1000_nodes_connected.json",  # Connected large-scale dataset
    "max_nodes": 1000,                     # ACTUAL EdgeServers with connected topology
    "enable_extreme_scale": True           # enable extreme scale features for large dataset
}


# File paths
FILES_CONFIG = {
    "results_dir": "results/"
}

# Privacy/DP settings for PPO.federated_average and gradient clipping
DP_CONFIG = {
    "noise_scale": 1.0,   # standard deviation for Gaussian noise in FedAvg
    "clip_norm":   0.5    # max norm for gradient clipping in PPO.update()
}

# PPO hyperparameters
PPO_CONFIG = {
    "clip_epsilon":   0.2,    # PPO clipping epsilon
    "entropy_coef":   0.01,   # weight on entropy bonus (from best config)
    "learning_rate":  0.001,  # Adam learning rate (from best config)
    "update_epochs":  4       # number of epochs per PPO update
}


# Hierarchical federation sync intervals (in epochs)
HIER_PARAMS = {
    "intra_sync": 10,    # epochs between intra‐cluster FedAvg (more frequent for stability)
    "inter_sync": 50,    # epochs between all‐nodes FedAvg (more frequent for stability)
    "num_clusters": 10,    # how many clusters to partition into
    "hidden_dim": 64,
    "graph_type": "mesh",
    "K1": 10,   # intra-cluster sync interval (more frequent)
    "K2": 50,   # inter-cluster sync interval (more frequent)
    "base_cluster_size": 100,              # base cluster size for extreme scale
    "max_cluster_size": 200,               # maximum cluster size
    "min_cluster_size": 20,                # minimum cluster size
    "reclustering_interval": 50            # epochs between adaptive reclustering
}

# Semantic feature extractor
SEMANTIC_CONFIG = {
    "match_threshold": 0.3,  # Lower threshold for realistic semantic mismatches
    "semantic_dim": 16,
    # Optional: priority-aware similarity threshold adaptation.
    # Keep slope at 0.0 to preserve legacy behavior; sensitivity experiments can override.
    "priority_threshold_slope": 0.0,
}

# Extreme Scale Federation Configuration
EXTREME_SCALE_CONFIG = {
    "compression_ratio": 0.1,             # target compression ratio (10%)
    "quantization_bits": 8,               # bits for weight quantization
    "sparsity_threshold": 0.01,           # threshold for gradient sparsification
    "use_top_k": True,                    # enable top-k gradient selection
    "k_ratio": 0.1,                       # ratio of top gradients to keep (10%)
    "staleness_threshold": 10,            # maximum allowed gradient staleness
    "similarity_threshold": 0.7,          # cluster similarity threshold
    "communication_scheduling": True,     # enable adaptive communication scheduling
    "hierarchical_compression": True,     # enable hierarchical model compression
    "selective_exchange": True,           # enable selective parameter exchange
    "asynchronous_updates": True          # enable asynchronous update handling
}