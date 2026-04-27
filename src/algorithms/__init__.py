# src/algorithms/__init__.py
"""
Algorithm implementations for FedSemGNN.

This package contains various federated learning algorithms and enhancement modules.
"""

# Import key algorithms for easier access
try:
    # Import available algorithms - graceful handling if modules are missing
    __all__ = []
    
    # Try to import specific algorithms as they are available
    try:
        from . import fedavg
        __all__.append('fedavg')
    except ImportError:
        pass
        
    try:
        from . import fednova
        __all__.append('fednova')
    except ImportError:
        pass
        
    try:
        from . import fedprox
        __all__.append('fedprox')
    except ImportError:
        pass
        
    try:
        from . import scaffold
        __all__.append('scaffold')
    except ImportError:
        pass
        
except ImportError:
    __all__ = []