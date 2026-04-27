"""
Patch point for scalable topology injection.
If --use-generated-topology is set, this module will generate a topology and provide it to the simulation.
"""
import argparse
from tools.topology_generator import get_topology

# Example usage: import and call get_topology(num_nodes, mode, ...)
# This file can be imported in your algorithm scripts or dataset loader.

def maybe_generate_topology(args, num_nodes):
    """
    If args.use_generated_topology is set, return a generated topology (list of NetworkLink dicts).
    Otherwise, return None (use dataset as usual).
    """
    if hasattr(args, 'use_generated_topology') and args.use_generated_topology:
        mode = getattr(args, 'topology_mode', 'ring')
        degree = getattr(args, 'topology_degree', 4)
        # You can add more kwargs as needed
        return get_topology(num_nodes, mode=mode, degree=degree)
    return None
