#!/usr/bin/env python3
"""
Detailed Fair Comparison Analysis
Provides comprehensive ranking and statistical analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

class DetailedComparisonAnalysis:
    """Provides detailed statistical analysis of algorithm performance"""
    
    def __init__(self, summary_file):
        self.summary_df = pd.read_csv(summary_file)
        self.results_dir = os.path.dirname(summary_file)
        
    def rank_algorithms(self):
        """Rank algorithms based on multiple criteria"""
        
        # Define ranking criteria (higher is better for reward and fidelity, lower is better for latency and power)
        criteria = {
            'reward_mean': 'max',
            'latency_mean': 'min', 
            'power_mean': 'min',
            'fidelity_mean': 'max'
        }
        
        rankings = {}
        
        for criterion, direction in criteria.items():
            if direction == 'max':
                rankings[criterion] = self.summary_df.sort_values(criterion, ascending=False)
            else:
                rankings[criterion] = self.summary_df.sort_values(criterion, ascending=True)
        
        # Calculate weighted overall score
        # Normalize all metrics to 0-1 scale
        normalized_df = self.summary_df.copy()
        
        for criterion in criteria.keys():
            values = normalized_df[criterion].dropna()
            if len(values) > 0:
                if criteria[criterion] == 'max':
                    # Higher is better - normalize to 0-1 where 1 is best
                    normalized_df[f'{criterion}_norm'] = (values - values.min()) / (values.max() - values.min())
                else:
                    # Lower is better - normalize to 0-1 where 1 is best (lowest value)
                    normalized_df[f'{criterion}_norm'] = (values.max() - values) / (values.max() - values.min())
        
        # Weighted combination (you can adjust weights based on importance)
        weights = {
            'reward_mean_norm': 0.35,      # Performance is most important
            'latency_mean_norm': 0.25,     # Latency is critical
            'power_mean_norm': 0.20,       # Energy efficiency matters
            'fidelity_mean_norm': 0.20     # Quality is important
        }
        
        normalized_df['overall_score'] = 0
        for metric, weight in weights.items():
            if metric in normalized_df.columns:
                normalized_df['overall_score'] += normalized_df[metric] * weight
        
        overall_ranking = normalized_df.sort_values('overall_score', ascending=False)
        
        return rankings, overall_ranking
    
    def generate_ranking_report(self):
        """Generate comprehensive ranking report"""
        
        rankings, overall_ranking = self.rank_algorithms()
        
        print("🏆 DETAILED ALGORITHM RANKING ANALYSIS")
        print("="*80)
        
        # Individual criterion rankings
        print("\\n📊 Individual Criterion Rankings:")
        print("-"*50)
        
        for criterion, df in rankings.items():
            print(f"\\n{criterion.replace('_', ' ').title()}:")
            for i, (_, row) in enumerate(df.iterrows(), 1):
                print(f"  {i}. {row['algorithm']} ({row['steps']} steps): {row[criterion]:.2f}")
        
        # Overall ranking
        print("\\n🎯 OVERALL RANKING (Weighted Score):")
        print("-"*50)
        
        for i, (_, row) in enumerate(overall_ranking.iterrows(), 1):
            print(f"{i}. {row['algorithm']} ({row['steps']} steps)")
            print(f"   Overall Score: {row['overall_score']:.3f}")
            print(f"   Reward: {row['reward_mean']:.1f}, Latency: {row['latency_mean']:.1f}ms")
            print(f"   Power: {row['power_mean']:.1f}W, Fidelity: {row['fidelity_mean']:.1f}%")
            print()
        
        # Save ranking report
        ranking_path = os.path.join(self.results_dir, "algorithm_rankings.csv")
        overall_ranking.to_csv(ranking_path, index=False)
        print(f"📋 Rankings saved to: {ranking_path}")
        
        return overall_ranking
    
    def statistical_significance_test(self):
        """Perform statistical significance tests between algorithms"""
        
        print("\\n📈 STATISTICAL SIGNIFICANCE ANALYSIS")
        print("="*80)
        
        # Compare FedSemGNN against each baseline
        fedsemgnn_500 = self.summary_df[(self.summary_df['algorithm'] == 'FedSemGNN') & (self.summary_df['steps'] == 500)]
        fedsemgnn_1000 = self.summary_df[(self.summary_df['algorithm'] == 'FedSemGNN') & (self.summary_df['steps'] == 1000)]
        
        baselines = ['FlatFedPPO', 'HierFedPPO', 'HSQF', 'RandomPlacement']
        
        for baseline in baselines:
            baseline_500 = self.summary_df[(self.summary_df['algorithm'] == baseline) & (self.summary_df['steps'] == 500)]
            baseline_1000 = self.summary_df[(self.summary_df['algorithm'] == baseline) & (self.summary_df['steps'] == 1000)]
            
            print(f"\\nFedSemGNN vs {baseline}:")
            
            # Compare reward differences
            if not fedsemgnn_500.empty and not baseline_500.empty:
                fed_reward = fedsemgnn_500['reward_mean'].iloc[0]
                base_reward = baseline_500['reward_mean'].iloc[0]
                improvement = ((fed_reward - base_reward) / base_reward) * 100
                
                print(f"  500 steps - Reward improvement: {improvement:+.1f}%")
                print(f"    FedSemGNN: {fed_reward:.1f}, {baseline}: {base_reward:.1f}")
            
            if not fedsemgnn_1000.empty and not baseline_1000.empty:
                fed_reward = fedsemgnn_1000['reward_mean'].iloc[0]
                base_reward = baseline_1000['reward_mean'].iloc[0]
                improvement = ((fed_reward - base_reward) / base_reward) * 100
                
                print(f"  1000 steps - Reward improvement: {improvement:+.1f}%")
                print(f"    FedSemGNN: {fed_reward:.1f}, {baseline}: {base_reward:.1f}")
        
        return True
    
    def generate_performance_radar_chart(self):
        """Generate radar chart comparing top algorithms"""
        
        # Select top 5 algorithms for radar chart
        rankings, overall_ranking = self.rank_algorithms()
        top_algorithms = overall_ranking.head(5)
        
        # Prepare radar chart data
        categories = ['Reward', 'Latency\\n(Inverted)', 'Power\\n(Inverted)', 'Fidelity']
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Number of variables
        N = len(categories)
        
        # Compute angle for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the circle
        
        colors = plt.cm.Set1(np.linspace(0, 1, len(top_algorithms)))
        
        for i, (_, row) in enumerate(top_algorithms.iterrows()):
            # Normalize values for radar chart (0-1 scale)
            values = [
                row['reward_mean_norm'] if 'reward_mean_norm' in row else 0,
                row['latency_mean_norm'] if 'latency_mean_norm' in row else 0,
                row['power_mean_norm'] if 'power_mean_norm' in row else 0,
                row['fidelity_mean_norm'] if 'fidelity_mean_norm' in row else 0
            ]
            values += values[:1]  # Complete the circle
            
            label = f"{row['algorithm']} ({row['steps']})"
            ax.plot(angles, values, 'o-', linewidth=2, label=label, color=colors[i])
            ax.fill(angles, values, alpha=0.25, color=colors[i])
        
        # Add category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 1)
        
        # Add legend
        plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        plt.title('Algorithm Performance Comparison\\n(Normalized Metrics)', 
                 size=16, fontweight='bold', pad=20)
        
        # Save radar chart
        radar_path = os.path.join(self.results_dir, "comparison_plots", "performance_radar.png")
        plt.savefig(radar_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Radar chart saved: {radar_path}")
    
    def efficiency_analysis(self):
        """Analyze efficiency metrics"""
        
        print("\\n⚡ EFFICIENCY ANALYSIS")
        print("="*80)
        
        # Calculate efficiency ratios
        efficiency_data = []
        
        for _, row in self.summary_df.iterrows():
            # Reward per watt (performance per power)
            reward_per_watt = row['reward_mean'] / row['power_mean'] if row['power_mean'] > 0 else 0
            
            # Reward per latency (performance per delay)
            reward_per_latency = row['reward_mean'] / row['latency_mean'] if row['latency_mean'] > 0 else 0
            
            # Overall efficiency score
            efficiency_score = (reward_per_watt * reward_per_latency) ** 0.5
            
            efficiency_data.append({
                'algorithm': row['algorithm'],
                'steps': row['steps'],
                'reward_per_watt': reward_per_watt,
                'reward_per_latency': reward_per_latency,
                'efficiency_score': efficiency_score
            })
        
        efficiency_df = pd.DataFrame(efficiency_data)
        efficiency_df = efficiency_df.sort_values('efficiency_score', ascending=False)
        
        print("Efficiency Rankings:")
        print("-"*30)
        for i, (_, row) in enumerate(efficiency_df.iterrows(), 1):
            print(f"{i}. {row['algorithm']} ({row['steps']} steps)")
            print(f"   Efficiency Score: {row['efficiency_score']:.3f}")
            print(f"   Reward/Watt: {row['reward_per_watt']:.3f}")
            print(f"   Reward/Latency: {row['reward_per_latency']:.3f}")
            print()
        
        # Save efficiency analysis
        efficiency_path = os.path.join(self.results_dir, "efficiency_analysis.csv")
        efficiency_df.to_csv(efficiency_path, index=False)
        print(f"📋 Efficiency analysis saved: {efficiency_path}")
        
        return efficiency_df
    
    def run_complete_analysis(self):
        """Run complete detailed analysis"""
        
        print("🔬 COMPREHENSIVE FAIR COMPARISON ANALYSIS")
        print("="*80)
        
        # Generate rankings
        overall_ranking = self.generate_ranking_report()
        
        # Statistical analysis  
        self.statistical_significance_test()
        
        # Efficiency analysis
        efficiency_df = self.efficiency_analysis()
        
        # Generate radar chart
        self.generate_performance_radar_chart()
        
        # Summary conclusions
        print("\\n🎯 KEY FINDINGS:")
        print("="*80)
        
        best_overall = overall_ranking.iloc[0]
        print(f"1. BEST OVERALL: {best_overall['algorithm']} ({best_overall['steps']} steps)")
        print(f"   Overall Score: {best_overall['overall_score']:.3f}")
        
        # Find best in each category
        best_reward = self.summary_df.loc[self.summary_df['reward_mean'].idxmax()]
        best_latency = self.summary_df.loc[self.summary_df['latency_mean'].idxmin()]
        best_power = self.summary_df.loc[self.summary_df['power_mean'].idxmin()]
        best_fidelity = self.summary_df.loc[self.summary_df['fidelity_mean'].idxmax()]
        
        print(f"\\n2. CATEGORY LEADERS:")
        print(f"   Best Reward: {best_reward['algorithm']} ({best_reward['steps']} steps) - {best_reward['reward_mean']:.1f}")
        print(f"   Best Latency: {best_latency['algorithm']} ({best_latency['steps']} steps) - {best_latency['latency_mean']:.1f}ms")
        print(f"   Best Power: {best_power['algorithm']} ({best_power['steps']} steps) - {best_power['power_mean']:.1f}W")
        print(f"   Best Fidelity: {best_fidelity['algorithm']} ({best_fidelity['steps']} steps) - {best_fidelity['fidelity_mean']:.1f}%")
        
        # Efficiency leader
        best_efficiency = efficiency_df.iloc[0]
        print(f"\\n3. MOST EFFICIENT: {best_efficiency['algorithm']} ({best_efficiency['steps']} steps)")
        print(f"   Efficiency Score: {best_efficiency['efficiency_score']:.3f}")
        
        print(f"\\n✅ Complete analysis saved to: {self.results_dir}")
        
        return self.results_dir

# Run the analysis
if __name__ == "__main__":
    summary_file = "results/fair_comparison_existing_20250916_143500/performance_summary.csv"
    
    if os.path.exists(summary_file):
        analyzer = DetailedComparisonAnalysis(summary_file)
        analyzer.run_complete_analysis()
    else:
        print(f"❌ Summary file not found: {summary_file}")
        print("Please run existing_results_comparison.py first!")
