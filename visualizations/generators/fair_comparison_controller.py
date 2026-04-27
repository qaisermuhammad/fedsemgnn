#!/usr/bin/env python3
"""
Fair Comparison Controller for FedSemGNN vs Baselines
Ensures identical conditions across all algorithm runs
"""

import os
import sys
import subprocess
import shutil
import json
import time
from datetime import datetime
import pandas as pd

class FairComparisonController:
    """Controls run parameters to ensure fair comparison"""
    
    def __init__(self):
        self.algorithms = ["FedSemGNN", "FlatFedPPO", "HierFedPPO", "HSQF", "RandomPlacement"]
        self.steps = [500, 1000]
        self.encoders = ["gcn"]  # Focus on GCN for fair comparison
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
        self.results_dir = f"results/fair_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.results_dir, exist_ok=True)
        
    # Save configuration
    self.save_run_config()
    
    def save_run_config(self):
        """Save the run configuration for reproducibility"""
        config = {
            "timestamp": datetime.now().isoformat(),
            "algorithms": self.algorithms,
            "steps": self.steps,
            "encoders": self.encoders,
            "num_nodes": self.num_nodes,
            "random_seed": self.random_seed,
            "workload_config": self.workload_config,
            "python_version": sys.version,
            "platform": sys.platform
        }
        config_path = os.path.join(self.results_dir, "run_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"📋 Experiment configuration saved to: {config_path}")
    
    def run_single_experiment(self, algorithm, steps, encoder="gcn"):
        """Run a single algorithm with standardized parameters"""
        
        print(f"\n🚀 Running {algorithm} with {steps} steps, encoder={encoder}")
        
        # Create algorithm-specific results directory
        algo_dir = os.path.join(self.results_dir, f"{algorithm}_{encoder}_{steps}steps")
        os.makedirs(algo_dir, exist_ok=True)
        
        # Prepare standardized command arguments
        base_args = [
            "--steps", str(steps),
            "--encoder", encoder,
            "--override-num-nodes", str(self.num_nodes),
            "--output-dir", algo_dir,
            "--random-seed", str(self.random_seed),
        ]
        
        # Add workload configuration
        for key, value in self.workload_config.items():
            base_args.extend([f"--{key.replace('_', '-')}", str(value)])
        
        start_time = time.time()
        
        try:
            if algorithm == "FedSemGNN":
                # Run enhanced FedSemGNN
                cmd = [sys.executable, "FedSemGNN.py"] + base_args + ["--algo", algorithm]
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                
            else:
                # Run baseline algorithms
                script_map = {
                    "FlatFedPPO": "flat_fedppo.py",
                    "HierFedPPO": "hier_fedppo.py", 
                    "HSQF": "hsqf.py",
                    "RandomPlacement": "random_place.py"
                }
                
                script = script_map[algorithm]
                cmd = [sys.executable, script] + base_args
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                
                # Move default output to algorithm directory
                default_csv = f"results/{algorithm.lower()}_metrics.csv"
                if os.path.exists(default_csv):
                    target_csv = os.path.join(algo_dir, "metrics.csv")
                    shutil.move(default_csv, target_csv)
            
            elapsed_time = time.time() - start_time
            
            # Record success
            result_info = {
                "algorithm": algorithm,
                "steps": steps,
                "encoder": encoder,
                "status": "success",
                "runtime_seconds": elapsed_time,
                "timestamp": datetime.now().isoformat(),
                "output_dir": algo_dir
            }
            
            print(f"✅ {algorithm} completed in {elapsed_time:.2f}s")
            return result_info
            
        except subprocess.CalledProcessError as e:
            elapsed_time = time.time() - start_time
            print(f"❌ {algorithm} failed after {elapsed_time:.2f}s")
            print(f"   Error: {e}")
            if hasattr(e, 'stdout') and e.stdout:
                print(f"   STDOUT: {e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"   STDERR: {e.stderr}")
            
            result_info = {
                "algorithm": algorithm,
                "steps": steps,
                "encoder": encoder,
                "status": "failed",
                "runtime_seconds": elapsed_time,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return result_info
    
    def run_full_comparison(self):
        """Run complete fair comparison across all algorithms"""
        
        print("🎯 Starting Fair Comparison Experiment")
        print("="*60)
        print(f"Algorithms: {self.algorithms}")
        print(f"Steps: {self.steps}")
        print(f"Encoders: {self.encoders}")
        print(f"Nodes: {self.num_nodes}")
        print(f"Random Seed: {self.random_seed}")
        print(f"Results Directory: {self.results_dir}")
        print("="*60)
        
        all_results = []
        total_experiments = len(self.algorithms) * len(self.steps) * len(self.encoders)
        
        for steps in self.steps:
            for encoder in self.encoders:
                for i, algorithm in enumerate(self.algorithms):
                    current_exp = len(all_results) + 1
                    print(f"\n📊 Experiment {current_exp}/{total_experiments}")
                    
                    result = self.run_single_experiment(algorithm, steps, encoder)
                    all_results.append(result)
        
        # Save results summary
        results_df = pd.DataFrame(all_results)
        summary_path = os.path.join(self.results_dir, "experiment_summary.csv")
        results_df.to_csv(summary_path, index=False)
        
        # Print summary
        print(f"\n📈 EXPERIMENT SUMMARY")
        print("="*60)
        print(results_df.to_string(index=False))
        print(f"\nResults saved to: {self.results_dir}")
        
        # Check for failures
        failures = results_df[results_df['status'] == 'failed']
        if not failures.empty:
            print(f"\n⚠️  {len(failures)} experiments failed:")
            print(failures[['algorithm', 'steps', 'encoder', 'error']].to_string(index=False))
        else:
            print(f"\n✅ All {len(all_results)} experiments completed successfully!")
        
        return self.results_dir
    
    def generate_comparison_plots(self):
        """Generate fair comparison visualizations"""
        print(f"\n📊 Generating comparison plots for: {self.results_dir}")
        
        # Update plot script to use our results
        plot_script = "plot_fair_comparison.py"
        self.create_plot_script(plot_script)
        
        # Run plotting
        subprocess.run([sys.executable, plot_script, "--results-dir", self.results_dir], check=True)

    def create_plot_script(self, script_name):
        """Create a plotting script specifically for fair comparison results"""
        script_content = f'''#!/usr/bin/env python3
"""
Fair Comparison Plotting Script
Automatically generated for results in: {self.results_dir}
"""

import os
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_fair_comparison(results_dir):
    """Generate comparison plots from fair comparison results"""
    
    algorithms = {self.algorithms}
    
    # Collect all metrics files
    metrics_data = {{}}
    
    for algo in algorithms:
        for steps in {self.steps}:
            key = f"{{algo}}_{{steps}}"
            metrics_file = os.path.join(results_dir, f"{{algo}}_gcn_{{steps}}steps", "metrics.csv")
            
            if not os.path.exists(metrics_file):
                metrics_file = os.path.join(results_dir, f"{{algo}}_gcn_{{steps}}steps", "fedsemgnn_metrics.csv")
            
            if os.path.exists(metrics_file):
                try:
                    df = pd.read_csv(metrics_file)
                    metrics_data[key] = df
                    print(f"✅ Loaded: {{key}} ({{len(df)}} rows)")
                except Exception as e:
                    print(f"❌ Failed to load {{key}}: {{e}}")
            else:
                print(f"⚠️  Missing: {{key}}")
    
    if not metrics_data:
        print("No metrics data found!")
        return
    
    # Create plots directory
    plots_dir = os.path.join(results_dir, "comparison_plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    # Plot performance metrics
    plt.figure(figsize=(15, 10))
    
    # Reward comparison
    plt.subplot(2, 3, 1)
    for key, df in metrics_data.items():
        if 'reward' in df.columns:
            plt.plot(df.index, df['reward'], label=key, alpha=0.8)
    plt.title('Reward Comparison')
    plt.xlabel('Step')
    plt.ylabel('Reward')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Latency comparison
    plt.subplot(2, 3, 2)
    for key, df in metrics_data.items():
        lat_col = None
        for col in df.columns:
            if 'latency' in col.lower():
                lat_col = col
                break
        if lat_col:
            plt.plot(df.index, df[lat_col], label=key, alpha=0.8)
    plt.title('Latency Comparison')
    plt.xlabel('Step')
    plt.ylabel('Latency (ms)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Power consumption
    plt.subplot(2, 3, 3)
    for key, df in metrics_data.items():
        if 'power' in df.columns:
            plt.plot(df.index, df['power'], label=key, alpha=0.8)
    plt.title('Power Consumption')
    plt.xlabel('Step')
    plt.ylabel('Power (W)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Fidelity comparison
    plt.subplot(2, 3, 4)
    for key, df in metrics_data.items():
        fid_col = None
        for col in df.columns:
            if 'fidelity' in col.lower():
                fid_col = col
                break
        if fid_col:
            plt.plot(df.index, df[fid_col], label=key, alpha=0.8)
    plt.title('Fidelity Comparison')
    plt.xlabel('Step')
    plt.ylabel('Fidelity (%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Bytes exchanged
    plt.subplot(2, 3, 5)
    for key, df in metrics_data.items():
        bytes_col = None
        for col in df.columns:
            if 'bytes' in col.lower():
                bytes_col = col
                break
        if bytes_col:
            plt.plot(df.index, df[bytes_col], label=key, alpha=0.8)
    plt.title('Communication Overhead')
    plt.xlabel('Step')
    plt.ylabel('Bytes Exchanged')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Summary statistics
    plt.subplot(2, 3, 6)
    summary_data = []
    for key, df in metrics_data.items():
        if 'reward' in df.columns:
            avg_reward = df['reward'].tail(100).mean()
            summary_data.append((key, avg_reward))
    
    if summary_data:
        keys, rewards = zip(*summary_data)
        bars = plt.bar(range(len(keys)), rewards)
        plt.xticks(range(len(keys)), keys, rotation=45)
        plt.title('Average Reward (Last 100 Steps)')
        plt.ylabel('Reward')
        
        # Color bars
        colors = plt.cm.Set3(np.linspace(0, 1, len(bars)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)
    
    plt.tight_layout()
    plot_file = os.path.join(plots_dir, "fair_comparison_metrics.png")
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Comparison plots saved to: {{plots_dir}}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True, help="Results directory from fair comparison")
    args = parser.parse_args()
    
    plot_fair_comparison(args.results_dir)
'''
        
        with open(script_name, 'w') as f:
            f.write(script_content)

if __name__ == "__main__":
    controller = FairComparisonController()
    results_dir = controller.run_full_comparison()
    controller.generate_comparison_plots()
    
    print(f"\\n🎯 Fair comparison complete!")
    print(f"Results available in: {{results_dir}}")
