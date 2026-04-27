#!/usr/bin/env python3
"""
1000-Step Only Fair Comparison
Focuses on realistic long-term performance without the suspicious 500-step results
"""

import os
import sys
import subprocess
import shutil
import json
import time
from datetime import datetime
import pandas as pd

class Fair1000StepComparison:
    """Controls 1000-step only run comparison"""
    
    def __init__(self):
        self.algorithms = ["FedSemGNN", "FlatFedPPO", "HierFedPPO", "HSQF", "RandomPlacement"]
        self.steps = 1000  # Only 1000 steps
        self.encoder = "gcn"  # Focus on GCN only
        self.num_nodes = 16  # Standardized
        self.random_seed = 42  # Fixed seed for reproducibility
        
        # Standardized workload parameters
        self.workload_config = {
            "num_services": 50,
            "service_arrival_rate": 0.1,
            "migration_threshold": 0.8,
            "power_budget": 3000,
            "latency_sla": 10.0,  # ms
            "bandwidth_limit": 1000,  # Mbps
            "cpu_capacity": 100,  # normalized
            "memory_capacity": 8192,  # MB
        }
        
        # Results tracking
        self.results_dir = f"results/fair_1000step_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Save configuration
    self.save_run_config()
    
    def save_run_config(self):
        """Save the run configuration for reproducibility"""
        config = {
            "timestamp": datetime.now().isoformat(),
            "algorithms": self.algorithms,
            "steps": self.steps,
            "encoder": self.encoder,
            "num_nodes": self.num_nodes,
            "random_seed": self.random_seed,
            "workload_config": self.workload_config,
            "python_version": sys.version,
            "platform": sys.platform,
            "purpose": "1000-step only comparison to address scalability issues"
        }
        
        config_path = os.path.join(self.results_dir, "experiment_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"📋 Experiment configuration saved to: {config_path}")
    
    def run_single_experiment(self, algorithm):
        """Run a single algorithm with 1000 steps"""
        
        print(f"\n🚀 Running {algorithm} with {self.steps} steps")
        
        # Create algorithm-specific results directory
        algo_dir = os.path.join(self.results_dir, f"{algorithm}_{self.encoder}_{self.steps}steps")
        os.makedirs(algo_dir, exist_ok=True)
        
        # Prepare algorithm-specific command arguments
        if algorithm == "FedSemGNN":
            # FedSemGNN supports: --steps, --encoder, --algo, --override-num-nodes, --output-dir
            fedsem_args = [
                "--steps", str(self.steps),
                "--encoder", self.encoder,
                "--override-num-nodes", str(self.num_nodes),
                "--output-dir", algo_dir,
                "--algo", algorithm
            ]
        else:
            # Baseline algorithms only accept --steps
            baseline_args = ["--steps", str(self.steps)]
        
        start_time = time.time()
        
        try:
            if algorithm == "FedSemGNN":
                # Run optimized FedSemGNN with correct virtual environment Python and full arguments
                python_exe = r"D:/FedSemGNN/FedSemGNN/.venv/Scripts/python.exe"
                cmd = [python_exe, "FedSemGNN.py"] + fedsem_args
                print(f"   Command: {' '.join(cmd[:3])} ... (with {len(cmd)-3} args)")
                
                result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)  # 1 hour timeout
                
            else:
                # Run baseline algorithms - check if they exist first
                script_map = {
                    "FlatFedPPO": "flat_fedppo.py",
                    "HierFedPPO": "hier_fedppo.py", 
                    "HSQF": "hsqf.py",
                    "RandomPlacement": "random_place.py"
                }
                
                script = script_map[algorithm]
                if not os.path.exists(script):
                    print(f"   ⚠️  Script {script} not found, skipping {algorithm}")
                    return {
                        "algorithm": algorithm,
                        "steps": self.steps,
                        "status": "skipped",
                        "error": f"Script {script} not found",
                        "timestamp": datetime.now().isoformat()
                    }
                
                python_exe = r"D:/FedSemGNN/FedSemGNN/.venv/Scripts/python.exe"
                # Baseline algorithms only accept --steps argument
                baseline_args = ["--steps", str(self.steps)]
                cmd = [python_exe, script] + baseline_args
                print(f"   Command: {' '.join(cmd[:3])} ... (with {len(cmd)-3} args)")
                
                result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)  # 1 hour timeout
                
                # Move default output to algorithm directory
                default_csv = f"results/{algorithm.lower()}_metrics.csv"
                if os.path.exists(default_csv):
                    target_csv = os.path.join(algo_dir, "metrics.csv")
                    shutil.move(default_csv, target_csv)
                    print(f"   📊 Moved metrics: {default_csv} → {target_csv}")
            
            elapsed_time = time.time() - start_time
            
            # Check if output files exist
            expected_files = ["fedsemgnn_metrics.csv", "fedsemgnn_trace.json"]
            found_files = []
            for exp_file in expected_files:
                file_path = os.path.join(algo_dir, exp_file)
                if os.path.exists(file_path):
                    found_files.append(exp_file)
            
            # Record success
            result_info = {
                "algorithm": algorithm,
                "steps": self.steps,
                "encoder": self.encoder,
                "status": "success",
                "runtime_seconds": elapsed_time,
                "output_files": found_files,
                "output_dir": algo_dir,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"   ✅ {algorithm} completed in {elapsed_time:.2f}s")
            if found_files:
                print(f"   📁 Output files: {', '.join(found_files)}")
            
            return result_info
            
        except subprocess.TimeoutExpired:
            elapsed_time = time.time() - start_time
            print(f"   ⏰ {algorithm} timed out after {elapsed_time:.2f}s")
            
            return {
                "algorithm": algorithm,
                "steps": self.steps,
                "status": "timeout",
                "runtime_seconds": elapsed_time,
                "error": "Process timed out after 1 hour",
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            elapsed_time = time.time() - start_time
            print(f"   ❌ {algorithm} failed after {elapsed_time:.2f}s")
            
            # Show last few lines of stderr for debugging
            if hasattr(e, 'stderr') and e.stderr:
                stderr_lines = e.stderr.strip().split('\n')
                print(f"   📋 Last error lines:")
                for line in stderr_lines[-3:]:  # Show last 3 lines
                    print(f"      {line}")
            
            result_info = {
                "algorithm": algorithm,
                "steps": self.steps,
                "status": "failed",
                "runtime_seconds": elapsed_time,
                "error": str(e),
                "stderr_snippet": stderr_lines[-3:] if hasattr(e, 'stderr') and e.stderr else [],
                "timestamp": datetime.now().isoformat()
            }
            return result_info
    
    def run_comparison(self):
        """Run complete 1000-step comparison across all algorithms"""
        
        print("🎯 Starting 1000-Step Only Fair Comparison")
        print("="*70)
        print(f"Algorithms: {self.algorithms}")
        print(f"Steps: {self.steps}")
        print(f"Encoder: {self.encoder}")
        print(f"Nodes: {self.num_nodes}")
        print(f"Random Seed: {self.random_seed}")
        print(f"Results Directory: {self.results_dir}")
        print("="*70)
        
        all_results = []
        
        for i, algorithm in enumerate(self.algorithms):
            print(f"\n📊 Experiment {i+1}/{len(self.algorithms)}: {algorithm}")
            
            result = self.run_single_experiment(algorithm)
            all_results.append(result)
            
            # Small delay between experiments
            time.sleep(2)
        
        # Save results summary
        results_df = pd.DataFrame(all_results)
        summary_path = os.path.join(self.results_dir, "experiment_summary.csv")
        results_df.to_csv(summary_path, index=False)
        
        # Print summary
        print(f"\n📈 EXPERIMENT SUMMARY")
        print("="*70)
        
        for _, row in results_df.iterrows():
            status_emoji = {"success": "✅", "failed": "❌", "timeout": "⏰", "skipped": "⚠️"}
            emoji = status_emoji.get(row['status'], "❓")
            print(f"{emoji} {row['algorithm']}: {row['status']} ({row['runtime_seconds']:.1f}s)")
            if row['status'] == 'success' and 'output_files' in row:
                print(f"   Files: {row.get('output_files', [])}")
            elif row['status'] in ['failed', 'timeout', 'skipped']:
                error = row.get('error', 'Unknown error')
                print(f"   Error: {error[:100]}{'...' if len(error) > 100 else ''}")
        
        print(f"\nResults saved to: {self.results_dir}")
        
        # Check for successful runs
        successes = results_df[results_df['status'] == 'success']
        failures = results_df[results_df['status'] != 'success']
        
        if not successes.empty:
            print(f"\n✅ {len(successes)} successful runs:")
            for _, row in successes.iterrows():
                print(f"   • {row['algorithm']}")
        
        if not failures.empty:
            print(f"\n❌ {len(failures)} failed/skipped runs:")
            for _, row in failures.iterrows():
                print(f"   • {row['algorithm']}: {row['status']}")
        
        return self.results_dir, len(successes) > 0

if __name__ == "__main__":
    controller = Fair1000StepComparison()
    results_dir, has_successes = controller.run_comparison()
    
    if has_successes:
        print(f"\n🎯 1000-step comparison complete!")
        print(f"Next: Run analysis on results in {results_dir}")
    else:
        print(f"\n⚠️  No successful runs. Check algorithms and dependencies.")
        print(f"Results (with errors) in: {results_dir}")
