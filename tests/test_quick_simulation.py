#test_quick_simulation.py

#!/usr/bin/env python3
"""
Quick test to verify simulation_trace structure by running just a few steps
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.getcwd())

from FedSemGNN import *

def test_quick_simulation():
    """Run a very short simulation to check trace structure."""
    
    print("Running quick simulation test...")
    
    # Initialize simulation_trace as dictionary 
    global simulation_trace
    simulation_trace = {'steps': []}
    
    print(f"Initial simulation_trace type: {type(simulation_trace)}")
    print(f"Initial simulation_trace: {simulation_trace}")
    
    # Simulate adding hardware energy metrics
    simulation_trace['hardware_energy_metrics'] = simulation_trace.get('hardware_energy_metrics', [])
    simulation_trace['hardware_energy_metrics'].append({
        'step': 1,
        'total_energy_j': 123.45,
        'test_metric': True
    })
    
    # Simulate adding extreme scale metrics
    simulation_trace['extreme_scale_metrics'] = simulation_trace.get('extreme_scale_metrics', [])
    simulation_trace['extreme_scale_metrics'].append({
        'step': 1,
        'efficiency': 0.85,
        'test_metric': True
    })
    
    # Simulate adding a step
    simulation_trace['steps'].append({
        'Step': 1,
        'SystemMetrics': {
            'Power': 100.0,
            'Reward': 1000.0
        }
    })
    
    print(f"After adding metrics - type: {type(simulation_trace)}")
    print(f"Keys: {list(simulation_trace.keys())}")
    print(f"Hardware metrics count: {len(simulation_trace['hardware_energy_metrics'])}")
    print(f"Extreme scale metrics count: {len(simulation_trace['extreme_scale_metrics'])}")
    print(f"Steps count: {len(simulation_trace['steps'])}")
    
    # Save test trace
    import json
    test_file = "test_trace_structure.json"
    with open(test_file, 'w') as f:
        json.dump(simulation_trace, f, indent=2)
    
    print(f"Test trace saved to: {test_file}")
    
    # Read it back to verify
    with open(test_file, 'r') as f:
        loaded_trace = json.load(f)
    
    print(f"Loaded trace type: {type(loaded_trace)}")
    print(f"Loaded trace keys: {list(loaded_trace.keys())}")
    
    return True

if __name__ == "__main__":
    test_quick_simulation()
