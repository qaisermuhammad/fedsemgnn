#!/usr/bin/env python3
"""
Fair Comparison with Existing Results
Uses standardized analysis of your existing experimental data
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import datetime

class ExistingResultsComparator:
    """Analyzes existing results for fair comparison"""
    
    def __init__(self):
        self.algorithms = ["FedSemGNN", "FlatFedPPO", "HierFedPPO", "HSQF", "RandomPlacement"]
        self.steps = [500, 1000]
        self.results_dir = f"results/fair_comparison_existing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Standardized metric mappings
        self.metric_mappings = {
            'reward': ['reward', 'reward_per_step', 'avg_reward'],
            'latency': ['latency_ms', 'latency_ms_e2e', 'lat_ms', 'latency'],
            'power': ['power', 'power_consumption', 'power_w'],
            'fidelity': ['fidelity_pct', 'fidelity', 'fidelity_percent'],
            'bytes': ['bytes_exchanged', 'cumulative_bytes', 'comm_bytes', 'bytes']
        }
    
    def find_metric_column(self, df, metric_type):
        """Find the correct column name for a metric type"""
        columns = [col.lower() for col in df.columns]
        for candidate in self.metric_mappings.get(metric_type, []):
            if candidate.lower() in columns:
                original_col = [col for col in df.columns if col.lower() == candidate.lower()][0]
                return original_col
        return None
    
    def load_existing_results(self):
        """Load all existing experimental results"""
        results = {}
        
        # Define where to find existing results
        result_paths = {
            "FedSemGNN_500": "results/FedSemGNN_gcn_500steps/fedsemgnn_metrics.csv",
            "FedSemGNN_1000": "results/FedSemGNN_gcn_1000steps/fedsemgnn_metrics.csv", 
            "FlatFedPPO_500": "results/FlatFedPPO_gcn_500steps/fedsemgnn_metrics.csv",
            "FlatFedPPO_1000": "results/FlatFedPPO_gcn_1000steps/fedsemgnn_metrics.csv",
            "HierFedPPO_500": "results/HierFedPPO_gcn_500steps/fedsemgnn_metrics.csv",
            "HierFedPPO_1000": "results/HierFedPPO_gcn_1000steps/fedsemgnn_metrics.csv",
            "HSQF_500": "results/HSQF_gcn_500steps/fedsemgnn_metrics.csv",
            "HSQF_1000": "results/HSQF_gcn_1000steps/fedsemgnn_metrics.csv",
            "RandomPlacement_500": "results/RandomPlacement_gcn_500steps/fedsemgnn_metrics.csv",
            "RandomPlacement_1000": "results/RandomPlacement_gcn_1000steps/fedsemgnn_metrics.csv"
        }
        
        # Alternative paths in case the structure is different
        alt_paths = {
            "FedSemGNN_500": "results/fedsemgnn_metrics.csv",  # Most recent run
            "FlatFedPPO_500": "results/flat_fedppo_metrics.csv",
            "FlatFedPPO_1000": "results/flat_fedppo_metrics.csv",
            "HierFedPPO_500": "results/hier_fedppo_metrics.csv", 
            "HierFedPPO_1000": "results/hier_fedppo_metrics.csv",
            "HSQF_500": "results/hsqf_metrics.csv",
            "HSQF_1000": "results/hsqf_metrics.csv",
            "RandomPlacement_500": "results/random_place_metrics.csv",
            "RandomPlacement_1000": "results/random_place_metrics.csv"
        }
        
        for key, path in result_paths.items():
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path)
                    results[key] = df
                    print(f"✅ Loaded {key}: {len(df)} rows from {path}")
                except Exception as e:
                    print(f"❌ Failed to load {key} from {path}: {e}")
            elif key in alt_paths and os.path.exists(alt_paths[key]):
                try:
                    df = pd.read_csv(alt_paths[key])
                    results[key] = df
                    print(f"✅ Loaded {key}: {len(df)} rows from {alt_paths[key]}")
                except Exception as e:
                    print(f"❌ Failed to load {key} from {alt_paths[key]}: {e}")
            else:
                print(f"⚠️  Missing: {key} (tried {path})")
        
        return results
    
    def normalize_metrics(self, results):
        """Normalize metrics for fair comparison"""
        normalized = {}
        
        for key, df in results.items():
            algo, steps = key.split('_')
            steps = int(steps)
            
            # Create standardized dataframe
            norm_df = pd.DataFrame()
            norm_df['step'] = range(len(df))
            norm_df['algorithm'] = algo
            norm_df['target_steps'] = steps
            
            # Map metrics using standardized names
            for metric_type in ['reward', 'latency', 'power', 'fidelity', 'bytes']:
                col = self.find_metric_column(df, metric_type)
                if col:
                    norm_df[metric_type] = df[col]
                    
                    # Apply normalizations
                    if metric_type == 'latency' and norm_df[metric_type].max() < 10:
                        # Convert seconds to milliseconds
                        norm_df[metric_type] *= 1000
                    elif metric_type == 'fidelity' and norm_df[metric_type].max() <= 1:
                        # Convert to percentage
                        norm_df[metric_type] *= 100
                    elif metric_type == 'bytes' and norm_df[metric_type].max() > 1e6:
                        # Convert to MB
                        norm_df[metric_type] /= (1024 * 1024)
                else:
                    norm_df[metric_type] = np.nan
                    print(f"⚠️  {key}: {metric_type} column not found")
            
            normalized[key] = norm_df
        
        return normalized
    
    def generate_comparison_plots(self, normalized_results):
        """Generate fair comparison visualizations"""
        
        # Create plots directory
        plots_dir = os.path.join(self.results_dir, "comparison_plots")
        os.makedirs(plots_dir, exist_ok=True)
        
        # Set up the figure
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Fair Algorithm Comparison - Existing Results', fontsize=16, fontweight='bold')
        
        metrics = ['reward', 'latency', 'power', 'fidelity', 'bytes']
        colors = plt.cm.Set1(np.linspace(0, 1, len(self.algorithms)))
        
        # Create color mapping
        color_map = {algo: color for algo, color in zip(self.algorithms, colors)}
        
        for i, metric in enumerate(metrics):
            row = i // 3
            col = i % 3
            ax = axes[row, col]
            
            # Plot each algorithm/steps combination
            for key, df in normalized_results.items():
                if not df[metric].isna().all():
                    algo, steps = key.split('_')
                    label = f"{algo} ({steps} steps)"
                    
                    # Smooth the data
                    smoothed = df[metric].rolling(window=5, min_periods=1).mean()
                    ax.plot(df['step'], smoothed, 
                           label=label, color=color_map[algo], 
                           alpha=0.8, linewidth=2)
            
            ax.set_title(f'{metric.title()} Comparison', fontweight='bold')
            ax.set_xlabel('Step')
            
            # Set appropriate y-label
            if metric == 'latency':
                ax.set_ylabel('Latency (ms)')
            elif metric == 'power':
                ax.set_ylabel('Power (W)')
            elif metric == 'fidelity':
                ax.set_ylabel('Fidelity (%)')
            elif metric == 'bytes':
                ax.set_ylabel('Bytes (MB)')
            else:
                ax.set_ylabel(metric.title())
            
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Summary statistics in the last subplot
        ax = axes[1, 2]
        self.plot_summary_statistics(normalized_results, ax)
        
        plt.tight_layout()
        plot_file = os.path.join(plots_dir, "fair_comparison_existing.png")
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Comparison plot saved: {plot_file}")
        
        # Generate individual metric plots
        self.generate_individual_plots(normalized_results, plots_dir)
    
    def plot_summary_statistics(self, normalized_results, ax):
        """Plot summary statistics"""
        summary_data = []
        
        for key, df in normalized_results.items():
            algo, steps = key.split('_')
            
            # Calculate averages over last 100 steps
            tail = df.tail(100)
            summary_data.append({
                'algorithm': algo,
                'steps': int(steps),
                'avg_reward': tail['reward'].mean() if not tail['reward'].isna().all() else 0,
                'avg_latency': tail['latency'].mean() if not tail['latency'].isna().all() else 0,
                'avg_power': tail['power'].mean() if not tail['power'].isna().all() else 0,
                'avg_fidelity': tail['fidelity'].mean() if not tail['fidelity'].isna().all() else 0
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        if not summary_df.empty:
            # Plot average reward
            algorithms = summary_df['algorithm'].unique()
            x_pos = np.arange(len(algorithms))
            
            for i, steps in enumerate([500, 1000]):
                step_data = summary_df[summary_df['steps'] == steps]
                rewards = [step_data[step_data['algorithm'] == algo]['avg_reward'].iloc[0] 
                          if not step_data[step_data['algorithm'] == algo].empty 
                          else 0 for algo in algorithms]
                
                ax.bar(x_pos + i*0.35, rewards, 0.35, 
                      label=f'{steps} steps', alpha=0.8)
            
            ax.set_xlabel('Algorithm')
            ax.set_ylabel('Average Reward (Last 100 steps)')
            ax.set_title('Performance Summary')
            ax.set_xticks(x_pos + 0.175)
            ax.set_xticklabels(algorithms, rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    def generate_individual_plots(self, normalized_results, plots_dir):
        """Generate individual metric plots"""
        metrics = ['reward', 'latency', 'power', 'fidelity', 'bytes']
        
        for metric in metrics:
            plt.figure(figsize=(12, 8))
            
            for key, df in normalized_results.items():
                if not df[metric].isna().all():
                    algo, steps = key.split('_')
                    label = f"{algo} ({steps} steps)"
                    
                    smoothed = df[metric].rolling(window=5, min_periods=1).mean()
                    plt.plot(df['step'], smoothed, label=label, alpha=0.8, linewidth=2)
            
            plt.title(f'{metric.title()} Comparison - All Algorithms', fontsize=14, fontweight='bold')
            plt.xlabel('Step')
            
            if metric == 'latency':
                plt.ylabel('Latency (ms)')
            elif metric == 'power':
                plt.ylabel('Power (W)')
            elif metric == 'fidelity':
                plt.ylabel('Fidelity (%)')
            elif metric == 'bytes':
                plt.ylabel('Bytes (MB)')
            else:
                plt.ylabel(metric.title())
            
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            plot_file = os.path.join(plots_dir, f"comparison_{metric}.png")
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 {metric.title()} plot saved: {plot_file}")
    
    def generate_performance_summary(self, normalized_results):
        """Generate comprehensive performance summary"""
        summary_data = []
        
        for key, df in normalized_results.items():
            algo, steps = key.split('_')
            
            # Calculate statistics
            stats = {}
            for metric in ['reward', 'latency', 'power', 'fidelity', 'bytes']:
                if not df[metric].isna().all():
                    series = df[metric].dropna()
                    stats[f'{metric}_mean'] = series.mean()
                    stats[f'{metric}_std'] = series.std()
                    stats[f'{metric}_final'] = series.iloc[-1] if len(series) > 0 else np.nan
                    stats[f'{metric}_best'] = series.max() if metric in ['reward', 'fidelity'] else series.min()
                else:
                    stats[f'{metric}_mean'] = np.nan
                    stats[f'{metric}_std'] = np.nan
                    stats[f'{metric}_final'] = np.nan
                    stats[f'{metric}_best'] = np.nan
            
            summary_data.append({
                'algorithm': algo,
                'steps': int(steps),
                'data_points': len(df),
                **stats
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        # Save summary
        summary_path = os.path.join(self.results_dir, "performance_summary.csv")
        summary_df.to_csv(summary_path, index=False)
        
        print(f"📋 Performance summary saved: {summary_path}")
        print("\\nPerformance Summary:")
        print("="*80)
        for _, row in summary_df.iterrows():
            print(f"{row['algorithm']} ({row['steps']} steps):")
            print(f"  Reward: {row['reward_mean']:.2f} ± {row['reward_std']:.2f}")
            print(f"  Latency: {row['latency_mean']:.2f} ± {row['latency_std']:.2f} ms")
            print(f"  Power: {row['power_mean']:.2f} ± {row['power_std']:.2f} W")
            print(f"  Fidelity: {row['fidelity_mean']:.2f} ± {row['fidelity_std']:.2f}%")
            print()
        
        return summary_df
    
    def run_comparison(self):
        """Run the complete existing results comparison"""
        print("🎯 Fair Comparison Using Existing Results")
        print("="*60)
        
        # Load existing results
        print("📂 Loading existing experimental results...")
        results = self.load_existing_results()
        
        if not results:
            print("❌ No existing results found!")
            return None
        
        # Normalize metrics
        print("\\n🔧 Normalizing metrics for fair comparison...")
        normalized = self.normalize_metrics(results)
        
        # Generate visualizations
        print("\\n📊 Generating comparison visualizations...")
        self.generate_comparison_plots(normalized)
        
        # Generate summary
        print("\\n📋 Generating performance summary...")
        summary = self.generate_performance_summary(normalized)
        
        print(f"\\n✅ Fair comparison complete!")
        print(f"Results saved to: {self.results_dir}")
        
        return self.results_dir

if __name__ == "__main__":
    comparator = ExistingResultsComparator()
    results_dir = comparator.run_comparison()
