# analysis/visualization/__init__.py
"""
Visualization modules for FedSemGNN analysis.

This package contains plotting and visualization functions for analyzing
federated learning results and metrics.
"""

# Import available visualization modules
try:
    __all__ = []
    
    # Try to import specific visualization modules as they are available
    try:
        from . import plot_cluster_rewards
        __all__.append('plot_cluster_rewards')
    except ImportError:
        pass
        
    try:
        from . import plot_diagnostics
        __all__.append('plot_diagnostics')
    except ImportError:
        pass
        
    try:
        from . import plot_energy_efficiency
        __all__.append('plot_energy_efficiency')
    except ImportError:
        pass
        
    try:
        from . import plot_convergence
        __all__.append('plot_convergence')
    except ImportError:
        pass
        
except ImportError:
    __all__ = []