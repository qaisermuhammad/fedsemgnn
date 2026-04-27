# config_1000_nodes.py
"""
Specialized configuration for 1000+ node extreme scale testing
As requested by supervisor for validating framework performance under extreme load
"""

REWARD_SCALE = 1000.0

# Extreme Scale Simulation Configuration (1000+ nodes)
SIMULATION_CONFIG = {
    "tick_duration": 1,
    "simulation_input": "extreme_scale_dataset_1000.json",  # Will generate this
    "max_nodes": 1000,                    # Target exactly 1000+ nodes
    "enable_extreme_scale": True,
    "target_node_count": 1000,            # Exact target for supervisor validation
    "validation_mode": True               # Enable detailed metrics collection
}

# Optimized for 1000-node federation
HIER_PARAMS = {
    # Clustering optimized for 1000 nodes
    "num_clusters": 20,                   # 20 clusters × 50 nodes = 1000 nodes
    "base_cluster_size": 50,              # Optimal size for 1000-node scenario
    "max_cluster_size": 75,               # Allow some flexibility
    "min_cluster_size": 25,               # Minimum viable cluster
    
    # Synchronization optimized for scale
    "intra_sync": 10,                     # More frequent intra-cluster sync
    "inter_sync": 50,                     # Less frequent global sync
    "K1": 10,                             # Intra-cluster sync interval
    "K2": 50,                             # Inter-cluster sync interval
    
    # Network topology
    "hidden_dim": 64,
    "graph_type": "hierarchical_mesh",    # Optimized for 1000 nodes
    "reclustering_interval": 100          # Adaptive reclustering
}

# Enhanced Extreme Scale Configuration for 1000 nodes
EXTREME_SCALE_CONFIG = {
    # Aggressive compression for 1000-node communication
    "compression_ratio": 0.05,            # 5% compression for better efficiency
    "quantization_bits": 4,               # More aggressive quantization
    "sparsity_threshold": 0.001,          # Lower threshold for sparsity
    
    # Top-K gradient selection
    "use_top_k": True,
    "k_ratio": 0.05,                      # Top 5% gradients only
    
    # Staleness management
    "staleness_threshold": 5,             # Stricter staleness for 1000 nodes
    "max_staleness_rounds": 3,            # Maximum stale rounds
    
    # Communication optimization
    "communication_scheduling": True,      # Essential for 1000 nodes
    "hierarchical_compression": True,     # Multi-level compression
    "selective_exchange": True,           # Only exchange significant updates
    "asynchronous_updates": True,         # Handle async updates
    
    # Adaptive clustering for 1000 nodes
    "adaptive_clustering": True,
    "similarity_threshold": 0.8,          # Higher similarity threshold
    "geographic_clustering": True,        # Use geographic proximity
    "workload_based_clustering": True,    # Cluster by workload similarity
    
    # Performance monitoring for validation
    "detailed_metrics": True,             # Collect comprehensive metrics
    "memory_monitoring": True,            # Monitor memory usage
    "communication_profiling": True,      # Profile communication overhead
    "convergence_tracking": True          # Track convergence at scale
}

# PPO Configuration optimized for extreme scale
PPO_CONFIG = {
    "clip_epsilon": 0.15,                 # Slightly more conservative
    "entropy_coef": 0.3,                  # Reduced entropy for stability
    "learning_rate": 1e-4,                # Lower LR for 1000-node stability
    "update_epochs": 2,                   # Fewer epochs to reduce overhead
    "batch_size": 32,                     # Smaller batches for memory efficiency
    "gradient_clip": 0.5                  # Gradient clipping for stability
}

# Semantic Configuration for large scale
SEMANTIC_CONFIG = {
    "match_threshold": 0.75,              # Higher threshold for precision
    "semantic_dim": 32,                   # Reduced dimension for efficiency
    "online_learning_rate": 0.0001,      # Conservative online learning
    "embedding_update_frequency": 20      # Less frequent updates
}

# Memory and Performance Configuration
PERFORMANCE_CONFIG = {
    "memory_limit_gb": 8,                 # 8GB memory limit
    "gradient_buffer_size": 100,          # Limit gradient buffer
    "trace_buffer_size": 500,             # Limit trace buffer
    "cleanup_frequency": 50,              # Clean up every 50 steps
    "checkpoint_frequency": 100,          # Checkpoint every 100 steps
    "early_stopping": True,               # Enable early stopping
    "convergence_patience": 50            # Steps to wait for convergence
}

# Validation and Testing Configuration
VALIDATION_CONFIG = {
    "enable_supervisor_metrics": True,    # Special metrics for supervisor validation
    "test_duration_steps": 500,           # Shorter test for initial validation
    "full_test_steps": 2000,              # Full test duration
    "performance_benchmarks": {
        "max_memory_gb": 8.0,             # Memory benchmark
        "max_communication_mb": 1000.0,   # Communication benchmark
        "min_convergence_rate": 0.95,     # Convergence benchmark
        "max_latency_ms": 100.0           # Latency benchmark
    }
}

# Files Configuration
FILES_CONFIG = {
    "results_dir": "results/extreme_scale_1000_nodes/",
    "metrics_file": "extreme_scale_metrics_1000.csv",
    "trace_file": "extreme_scale_trace_1000.json",
    "model_checkpoint": "model_checkpoint_1000.pth"
}

# Privacy/DP settings optimized for 1000 nodes
DP_CONFIG = {
    "noise_scale": 0.5,                   # Reduced noise for 1000-node stability
    "clip_norm": 1.0                      # Higher clip norm for gradient diversity
}

# Logging Configuration for extreme scale testing
LOGGING_CONFIG = {
    "log_level": "INFO",
    "enable_detailed_logging": True,
    "log_communication": True,
    "log_clustering": True,
    "log_compression": True,
    "max_log_size_mb": 100
}

print("✅ Loaded 1000-node extreme scale configuration")
print(f"   Target nodes: {SIMULATION_CONFIG['target_node_count']}")
print(f"   Clusters: {HIER_PARAMS['num_clusters']}")
print(f"   Cluster size: {HIER_PARAMS['base_cluster_size']}")
print(f"   Compression ratio: {EXTREME_SCALE_CONFIG['compression_ratio']}")