def StaticMobilityModel(user):
    # This model does nothing (static)
    pass
# semantic_utils.py

import numpy as np
import hashlib

# Handle imports with fallback for both relative and direct imports
try:
    from src.core.online_semantic_learning import extract_semantic_vector_online
except ImportError:
    def extract_semantic_vector_online(raw_id, **kwargs):
        """Fallback function when online semantic learning is not available"""
        return _extract_semantic_vector_hash(raw_id)


def _extract_semantic_vector_hash(raw_id, dim: int = 16) -> np.ndarray:
    """
    Deterministic semantic vector extractor.
    Uses hash of raw_id to generate a reproducible vector.
    """
    if raw_id is None:
        raw_id = "unknown"
    # Hash the id into a stable seed
    h = hashlib.md5(str(raw_id).encode()).hexdigest()
    seed = int(h[:8], 16)  # take first 8 hex chars
    rng = np.random.default_rng(seed)
    # Use strong normal distribution for diversity
    vec = rng.normal(0, 2.0, dim).astype(np.float32)
    # Normalize to unit vector
    return vec / np.linalg.norm(vec)


def extract_semantic_vector(obj):
    """
    Main semantic vector extraction function for FedSemGNN and related GNN-based algorithms.
    Routes to online semantic learning if available, otherwise uses hash-based fallback.
    Output: np.ndarray, typically used as node features for GNNEncoder.
    """
    try:
        return extract_semantic_vector_online(obj)
    except (NameError, AttributeError):
        # Fallback to hash-based extraction
        # Always add extra randomization for EdgeServer objects
        if type(obj).__name__ == 'EdgeServer':
            # Use server id + salt for seed
            return _extract_semantic_vector_hash(str(obj) + '_server_salt', dim=16)
        else:
            return _extract_semantic_vector_hash(str(obj) + '_service_salt', dim=16)

# Alias for backward compatibility
extract_semantic_vectors = extract_semantic_vector
