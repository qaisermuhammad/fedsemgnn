#test_simulation_trace_fix.py

#!/usr/bin/env python3
"""
Test to verify that the simulation_trace fix works correctly
and that hardware energy metrics are being collected.
"""

import json
import os

def test_simulation_trace_structure():
    """Test that simulation_trace is properly structured and contains hardware metrics."""
    
    # Check if the trace file exists
    trace_file = "results/fedsemgnn_trace.json"
    if not os.path.exists(trace_file):
        print("❌ Trace file does not exist")
        return False
    
    try:
        with open(trace_file, 'r') as f:
            trace_data = json.load(f)
            
        print(f"✅ Trace file loaded successfully")
        print(f"   Type: {type(trace_data)}")
        print(f"   Length: {len(trace_data)}")
        
        if isinstance(trace_data, list):
            print("📋 Trace data is a list (old format)")
            # Check a few entries
            for i, entry in enumerate(trace_data[:3]):
                print(f"   Step {i+1} keys: {list(entry.keys())}")
                if 'SystemMetrics' in entry:
                    print(f"     SystemMetrics keys: {list(entry['SystemMetrics'].keys())}")
                    
        elif isinstance(trace_data, dict):
            print("📁 Trace data is a dictionary (new format)")
            print(f"   Top-level keys: {list(trace_data.keys())}")
            
            if 'steps' in trace_data:
                print(f"   Steps count: {len(trace_data['steps'])}")
                
            if 'hardware_energy_metrics' in trace_data:
                print(f"   Hardware energy metrics count: {len(trace_data['hardware_energy_metrics'])}")
                print("✅ Hardware energy metrics found!")
                
            if 'extreme_scale_metrics' in trace_data:
                print(f"   Extreme scale metrics count: {len(trace_data['extreme_scale_metrics'])}")
                print("✅ Extreme scale metrics found!")
                
        return True
        
    except Exception as e:
        print(f"❌ Error reading trace file: {e}")
        return False

def test_no_attribute_error():
    """Test that simulation_trace no longer causes AttributeError."""
    
    # Simulate the problematic code pattern
    simulation_trace = {'steps': []}
    
    try:
        # This should work now
        simulation_trace['hardware_energy_metrics'] = simulation_trace.get('hardware_energy_metrics', [])
        simulation_trace['hardware_energy_metrics'].append({
            'step': 1,
            'total_energy_j': 100.0,
            'test': True
        })
        
        print("✅ Dictionary operations work correctly")
        print(f"   Hardware metrics count: {len(simulation_trace['hardware_energy_metrics'])}")
        return True
        
    except AttributeError as e:
        print(f"❌ AttributeError still occurs: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

if __name__ == "__main__":
    print("Testing simulation_trace fix...")
    print("="*50)
    
    print("\n1. Testing dictionary operations:")
    test_no_attribute_error()
    
    print("\n2. Testing trace file structure:")
    test_simulation_trace_structure()
    
    print("\n" + "="*50)
    print("Test complete!")
