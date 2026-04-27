# analysis/metrics/__init__.py
"""
Metrics calculation modules for FedSemGNN analysis.

This package contains various metrics computation modules for evaluating
federated learning performance.
"""

# Import available metrics modules
try:
    __all__ = []
    
    # Try to import specific metrics modules as they are available
    try:
        from . import energy_metrics
        __all__.append('energy_metrics')
    except ImportError:
        pass
        
    try:
        from . import performance_metrics
        __all__.append('performance_metrics')
    except ImportError:
        pass
        
    try:
        from . import scalability_metrics
        __all__.append('scalability_metrics')
    except ImportError:
        pass
        
except ImportError:
    __all__ = []