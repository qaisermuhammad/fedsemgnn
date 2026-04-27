# src/utils/__init__.py
"""
Utility modules for FedSemGNN framework.

This package contains utility functions for semantic processing, performance monitoring,
and various helper functions.
"""

# Import commonly used utilities for easier access
try:
    from .semantic_utils import extract_semantic_vectors
    from .step_latency_instrument import log_step_latency
    __all__ = ['extract_semantic_vectors', 'log_step_latency']
except ImportError:
    # Handle cases where dependencies are not available
    __all__ = []