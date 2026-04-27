# src/core/__init__.py
"""
Core algorithms and configuration for FedSemGNN.

This package contains the main FedSemGNN algorithm and all enhancement modules.
"""

# Import main components for easier access
try:
    from .config import SIMULATION_CONFIG, HIER_PARAMS, SEMANTIC_CONFIG
    from .FedSemGNN import fedsemgnn_algorithm
    __all__ = ['SIMULATION_CONFIG', 'HIER_PARAMS', 'SEMANTIC_CONFIG', 'fedsemgnn_algorithm']
except ImportError:
    # Handle cases where dependencies are not available
    __all__ = []