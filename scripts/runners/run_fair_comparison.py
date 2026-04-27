#!/usr/bin/env python3
"""
Fair Comparison Experiment Script
Runs all algorithms with identical conditions for scientific comparison
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime

def run_fair_comparison_experiment():
    """Run all algorithms with identical conditions for fair comparison"""
    
    print("🔬 FAIR COMPARISON EXPERIMENT")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Standardized experiment parameters
    experiment_config = {
        "steps": 100,  # Reduced for testing, use 1000 for final
        "override_num_nodes": 10000,
        "use_generated_topology": True,
        "topology_mode": "random",
        "topology_degree": 8
    }
    
    algorithms = [
        "FedSemGNN",
        "FlatFedPPO", 
        "HierFedPPO",
        "HSQF",
        "RandomPlacement"
    ]
    
    results = {}
    
    print("🎯 EXPERIMENT CONFIGURATION:")
    print("-" * 40)
    for key, value in experiment_config.items():
        print(f"  {key}: {value}")
    print()
    
    # Clean up old results
    print("🧹 CLEANING OLD RESULTS...")
    for algo in algorithms:
        metrics_file = f"results/{algo.lower()}_metrics.csv"
        if os.path.exists(metrics_file):
            os.remove(metrics_file)
            print(f"  Removed old {metrics_file}")
    print()
    
    # Run each algorithm
    for i, algorithm in enumerate(algorithms, 1):
        print(f"📊 RUNNING ALGORITHM {i}/{len(algorithms)}: {algorithm}")
        print("-" * 40)
        
        # Build command
        cmd = [
            sys.executable, "main.py",
            "--steps", str(experiment_config["steps"]),
            "--algorithm", algorithm,
            "--override-num-nodes", str(experiment_config["override_num_nodes"])
        ]
        
        if experiment_config["use_generated_topology"]:
            cmd.extend([
                "--use-generated-topology",
                "--topology-mode", experiment_config["topology_mode"],
                "--topology-degree", str(experiment_config["topology_degree"])
            ])
        
        print(f"Command: {' '.join(cmd)}")
        
        # Run the algorithm
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 min timeout
            runtime = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ {algorithm} completed successfully in {runtime:.1f}s")
                results[algorithm] = {
                    "status": "success",
                    "runtime": runtime,
                    "stdout_lines": len(result.stdout.split('\n')),
                    "stderr_lines": len(result.stderr.split('\n'))
                }
            else:
                print(f"❌ {algorithm} failed with return code {result.returncode}")
                print("STDERR:", result.stderr[-500:])  # Last 500 chars of error
                results[algorithm] = {
                    "status": "failed",
                    "error": result.stderr[-200:],
                    "runtime": runtime
                }
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {algorithm} timed out after 5 minutes")
            results[algorithm] = {
                "status": "timeout",
                "runtime": 300.0
            }
        except Exception as e:
            print(f"💥 {algorithm} crashed: {str(e)}")
            results[algorithm] = {
                "status": "crashed",
                "error": str(e),
                "runtime": time.time() - start_time
            }
        
        print()
    
    # Summary
    print("📋 EXPERIMENT SUMMARY:")
    print("=" * 60)
    
    successful = [algo for algo, result in results.items() if result["status"] == "success"]
    failed = [algo for algo, result in results.items() if result["status"] != "success"]
    
    print(f"✅ Successful: {len(successful)}/{len(algorithms)}")
    for algo in successful:
        runtime = results[algo]["runtime"]
        print(f"   {algo}: {runtime:.1f}s")
    
    if failed:
        print(f"❌ Failed: {len(failed)}/{len(algorithms)}")
        for algo in failed:
            status = results[algo]["status"]
            print(f"   {algo}: {status}")
    
    print()
    
    # Check for generated results
    print("📁 GENERATED RESULTS:")
    print("-" * 40)
    for algo in algorithms:
        metrics_file = f"results/{algo.lower()}_metrics.csv"
        if os.path.exists(metrics_file):
            size = os.path.getsize(metrics_file)
            print(f"✅ {metrics_file}: {size:,} bytes")
        else:
            print(f"❌ {metrics_file}: missing")
    
    print()
    print("🎉 Fair comparison experiment completed!")
    print(f"Next step: Run 'python generate_all_graphs.py' to create fair comparison visualizations")
    
    return results

if __name__ == "__main__":
    try:
        results = run_fair_comparison_experiment()
    except KeyboardInterrupt:
        print("\n\n⚠️  Experiment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Experiment failed: {str(e)}")
        sys.exit(1)