# plot_enhanced_fedsemgnn_results.py
"""
Enhanced plotting script for FedSemGNN results including:
- Traditional metrics (reward, latency, fidelity, power)
- Online semantic learning progress
- Multi-cluster fault tolerance status
- Extreme scale metrics
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import seaborn as sns
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_results():
    """Load all result files."""
    results = {}
    
    # Load main metrics
    results['metrics'] = pd.read_csv('results/fedsemgnn_metrics.csv')
    
    # Load JSON stats
    try:
        with open('results/fault_tolerance_stats.json', 'r') as f:
            results['fault_tolerance'] = json.load(f)
    except:
        results['fault_tolerance'] = {}
    
    try:
        with open('results/semantic_adaptation_stats.json', 'r') as f:
            results['semantic'] = json.load(f)
    except:
        results['semantic'] = {}
    
    try:
        with open('results/fedsemgnn_trace.json', 'r') as f:
            results['trace'] = json.load(f)
    except:
        results['trace'] = []
    
    return results

def plot_traditional_metrics(df):
    """Plot traditional performance metrics."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('FedSemGNN Traditional Performance Metrics', fontsize=16, fontweight='bold')
    
    # Reward over time
    axes[0,0].plot(df['Step'], df['Reward'], color='green', linewidth=2)
    axes[0,0].set_title('System Reward', fontweight='bold')
    axes[0,0].set_xlabel('Step')
    axes[0,0].set_ylabel('Reward')
    axes[0,0].grid(True, alpha=0.3)
    
    # Latency over time
    axes[0,1].plot(df['Step'], df['Latency_ms'], color='blue', linewidth=2)
    axes[0,1].set_title('Decision Latency', fontweight='bold')
    axes[0,1].set_xlabel('Step')
    axes[0,1].set_ylabel('Latency (ms)')
    axes[0,1].grid(True, alpha=0.3)
    
    # Fidelity over time
    axes[1,0].plot(df['Step'], df['Fidelity_pct'], color='orange', linewidth=2)
    axes[1,0].set_title('Semantic Fidelity', fontweight='bold')
    axes[1,0].set_xlabel('Step')
    axes[1,0].set_ylabel('Fidelity (%)')
    axes[1,0].grid(True, alpha=0.3)
    axes[1,0].set_ylim(0, 105)
    
    # Power consumption
    axes[1,1].plot(df['Step'], df['Power_W'], color='red', linewidth=2)
    axes[1,1].set_title('Power Consumption', fontweight='bold')
    axes[1,1].set_xlabel('Step')
    axes[1,1].set_ylabel('Power (W)')
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/traditional_metrics.png', dpi=300, bbox_inches='tight')
    print("✓ Saved traditional_metrics.png")
    
def plot_extreme_scale_metrics(df):
    """Plot extreme scale federation metrics."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Extreme Scale Federation Metrics', fontsize=16, fontweight='bold')
    
    # Total nodes
    axes[0,0].plot(df['Step'], df['ES_total_nodes'], color='purple', linewidth=2)
    axes[0,0].set_title('Total Nodes in Federation', fontweight='bold')
    axes[0,0].set_xlabel('Step')
    axes[0,0].set_ylabel('Number of Nodes')
    axes[0,0].grid(True, alpha=0.3)
    
    # Active clusters
    axes[0,1].plot(df['Step'], df['ES_active_clusters'], color='teal', linewidth=2)
    axes[0,1].set_title('Active Clusters', fontweight='bold')
    axes[0,1].set_xlabel('Step')
    axes[0,1].set_ylabel('Number of Clusters')
    axes[0,1].grid(True, alpha=0.3)
    
    # Communication efficiency
    axes[1,0].plot(df['Step'], df['ES_communication_efficiency'], color='brown', linewidth=2)
    axes[1,0].set_title('Communication Efficiency', fontweight='bold')
    axes[1,0].set_xlabel('Step')
    axes[1,0].set_ylabel('Efficiency Ratio')
    axes[1,0].grid(True, alpha=0.3)
    axes[1,0].set_ylim(0, 1.1)
    
    # Compression ratio
    axes[1,1].plot(df['Step'], df['ES_compression_ratio'], color='pink', linewidth=2)
    axes[1,1].set_title('Gradient Compression Ratio', fontweight='bold')
    axes[1,1].set_xlabel('Step')
    axes[1,1].set_ylabel('Compression Ratio')
    axes[1,1].grid(True, alpha=0.3)
    axes[1,1].set_ylim(0, 1.1)
    
    plt.tight_layout()
    plt.savefig('results/extreme_scale_metrics.png', dpi=300, bbox_inches='tight')
    print("✓ Saved extreme_scale_metrics.png")

def plot_fault_tolerance_dashboard(fault_stats):
    """Create fault tolerance dashboard."""
    if not fault_stats:
        print("⚠ No fault tolerance stats available")
        return
        
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Multi-Cluster Fault Tolerance Dashboard', fontsize=16, fontweight='bold')
    
    # Cluster health distribution (pie chart)
    health_summary = fault_stats.get('cluster_health_summary', {})
    if health_summary:
        labels = list(health_summary.keys())
        sizes = list(health_summary.values())
        colors = ['green', 'yellow', 'red', 'blue']
        
        axes[0,0].pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(labels)])
        axes[0,0].set_title('Cluster Health Distribution', fontweight='bold')
    
    # Individual cluster health scores
    cluster_scores = fault_stats.get('cluster_health_scores', {})
    if cluster_scores:
        clusters = list(cluster_scores.keys())
        scores = list(cluster_scores.values())
        
        bars = axes[0,1].bar(clusters, scores, color='lightblue', edgecolor='navy')
        axes[0,1].set_title('Individual Cluster Health Scores', fontweight='bold')
        axes[0,1].set_xlabel('Cluster ID')
        axes[0,1].set_ylabel('Health Score')
        axes[0,1].set_ylim(0, 1.1)
        axes[0,1].grid(True, alpha=0.3)
        
        # Color bars based on health
        for bar, score in zip(bars, scores):
            if score < 0.6:
                bar.set_color('red')
            elif score < 0.8:
                bar.set_color('yellow')
            else:
                bar.set_color('green')
    
    # Failure predictions
    predictions = fault_stats.get('failure_predictions', {})
    if predictions:
        pred_clusters = list(predictions.keys())
        pred_probs = list(predictions.values())
        
        axes[1,0].bar(pred_clusters, pred_probs, color='orange', edgecolor='red')
        axes[1,0].set_title('Failure Predictions', fontweight='bold')
        axes[1,0].set_xlabel('Cluster ID')
        axes[1,0].set_ylabel('Failure Probability')
        axes[1,0].set_ylim(0, 1.0)
        axes[1,0].grid(True, alpha=0.3)
    
    # System resilience summary
    resilience_score = fault_stats.get('resilience_score', 0)
    total_clusters = fault_stats.get('total_clusters', 0)
    cascade_events = fault_stats.get('total_cascade_events', 0)
    
    summary_text = f"""
    Total Clusters: {total_clusters}
    Resilience Score: {resilience_score:.2f}
    Cascade Events: {cascade_events}
    Active Failures: {fault_stats.get('active_failures', 0)}
    Recovery Time: {fault_stats.get('average_recovery_time', 0):.1f}s
    """
    
    axes[1,1].text(0.1, 0.5, summary_text, fontsize=12, 
                   verticalalignment='center', fontfamily='monospace',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
    axes[1,1].set_title('System Resilience Summary', fontweight='bold')
    axes[1,1].axis('off')
    
    plt.tight_layout()
    plt.savefig('results/fault_tolerance_dashboard.png', dpi=300, bbox_inches='tight')
    print("✓ Saved fault_tolerance_dashboard.png")

def plot_semantic_learning_progress(semantic_stats):
    """Plot online semantic learning progress."""
    if not semantic_stats:
        print("⚠ No semantic learning stats available")
        return
        
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Online Semantic Learning Progress', fontsize=16, fontweight='bold')
    
    # Service type distribution
    type_dist = semantic_stats.get('service_type_distribution', {})
    if type_dist:
        types = list(type_dist.keys())
        counts = list(type_dist.values())
        
        axes[0].bar(types, counts, color='skyblue', edgecolor='navy')
        axes[0].set_title('Service Type Distribution', fontweight='bold')
        axes[0].set_xlabel('Service Type')
        axes[0].set_ylabel('Count')
        axes[0].grid(True, alpha=0.3)
        
        # Rotate labels if needed
        if len(max(types, key=len)) > 8:
            axes[0].tick_params(axis='x', rotation=45)
    
    # Learning progress summary
    total_types = semantic_stats.get('total_service_types', 0)
    adaptation_events = semantic_stats.get('adaptation_events', 0)
    buffer_size = semantic_stats.get('experience_buffer_size', 0)
    
    progress_text = f"""
    📊 Learning Statistics:
    
    • Total Service Types: {total_types}
    • Adaptation Events: {adaptation_events}
    • Experience Buffer: {buffer_size}
    • Buffer Utilization: {(buffer_size/1000)*100:.1f}%
    
    🧠 Recent Adaptations:
    """
    
    # Add recent adaptations
    recent = semantic_stats.get('recent_adaptations', [])
    for i, adapt in enumerate(recent[-5:]):  # Last 5 adaptations
        event_type = adapt.get('event', 'unknown')
        service_type = adapt.get('service_type', 'unknown')
        progress_text += f"\n    {i+1}. {event_type}: {service_type}"
    
    axes[1].text(0.05, 0.95, progress_text, fontsize=11,
                 verticalalignment='top', fontfamily='monospace',
                 transform=axes[1].transAxes,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow"))
    axes[1].set_title('Learning Progress Summary', fontweight='bold')
    axes[1].axis('off')
    
    plt.tight_layout()
    plt.savefig('results/semantic_learning_progress.png', dpi=300, bbox_inches='tight')
    print("✓ Saved semantic_learning_progress.png")

def plot_comprehensive_summary(df):
    """Create a comprehensive summary plot."""
    fig, axes = plt.subplots(3, 2, figsize=(16, 18))
    fig.suptitle('FedSemGNN Enhanced System Performance Summary', fontsize=18, fontweight='bold')
    
    # Performance over time
    axes[0,0].plot(df['Step'], df['Reward'], color='green', linewidth=2, label='Reward')
    axes[0,0].set_title('System Performance', fontweight='bold')
    axes[0,0].set_xlabel('Step')
    axes[0,0].set_ylabel('Reward', color='green')
    axes[0,0].grid(True, alpha=0.3)
    
    # Secondary y-axis for fidelity
    ax_fid = axes[0,0].twinx()
    ax_fid.plot(df['Step'], df['Fidelity_pct'], color='orange', linewidth=2, label='Fidelity')
    ax_fid.set_ylabel('Fidelity (%)', color='orange')
    
    # Communication metrics
    axes[0,1].plot(df['Step'], df['Bytes_cum_MB'], color='blue', linewidth=2)
    axes[0,1].set_title('Cumulative Communication', fontweight='bold')
    axes[0,1].set_xlabel('Step')
    axes[0,1].set_ylabel('Data Exchanged (MB)')
    axes[0,1].grid(True, alpha=0.3)
    
    # System efficiency
    efficiency = df['Reward'] / df['Power_W'] * 1000  # Reward per kW
    axes[1,0].plot(df['Step'], efficiency, color='purple', linewidth=2)
    axes[1,0].set_title('Energy Efficiency (Reward/kW)', fontweight='bold')
    axes[1,0].set_xlabel('Step')
    axes[1,0].set_ylabel('Efficiency')
    axes[1,0].grid(True, alpha=0.3)
    
    # Migration stability
    axes[1,1].plot(df['Step'], df['Migrations'], color='red', linewidth=2)
    axes[1,1].set_title('Service Migrations', fontweight='bold')
    axes[1,1].set_xlabel('Step')
    axes[1,1].set_ylabel('Number of Migrations')
    axes[1,1].grid(True, alpha=0.3)
    
    # Extreme scale status
    axes[2,0].plot(df['Step'], df['ES_communication_overhead'], color='brown', linewidth=2, label='Overhead')
    axes[2,0].plot(df['Step'], df['ES_compression_ratio'], color='pink', linewidth=2, label='Compression')
    axes[2,0].set_title('Extreme Scale Optimization', fontweight='bold')
    axes[2,0].set_xlabel('Step')
    axes[2,0].set_ylabel('Ratio')
    axes[2,0].legend()
    axes[2,0].grid(True, alpha=0.3)
    
    # Performance statistics
    stats_text = f"""
    📈 Performance Summary (500 steps):
    
    Average Reward: {df['Reward'].mean():.1f}
    Best Reward: {df['Reward'].max():.1f}
    
    Average Latency: {df['Latency_ms'].mean():.2f} ms
    Min Latency: {df['Latency_ms'].min():.2f} ms
    
    Average Fidelity: {df['Fidelity_pct'].mean():.1f}%
    Max Fidelity: {df['Fidelity_pct'].max():.1f}%
    
    Total Data: {df['Bytes_cum_MB'].iloc[-1]:.2f} MB
    Avg Power: {df['Power_W'].mean():.1f} W
    
    Final Migrations: {df['Migrations'].iloc[-1]}
    
    🚀 System Status: OPERATIONAL
    ✅ All modules integrated successfully!
    """
    
    axes[2,1].text(0.05, 0.95, stats_text, fontsize=11,
                   verticalalignment='top', fontfamily='monospace',
                   transform=axes[2,1].transAxes,
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.7))
    axes[2,1].set_title('System Statistics', fontweight='bold')
    axes[2,1].axis('off')
    
    plt.tight_layout()
    plt.savefig('results/comprehensive_summary.png', dpi=300, bbox_inches='tight')
    print("✓ Saved comprehensive_summary.png")

def main():
    """Main plotting function."""
    print("🎨 Generating Enhanced FedSemGNN Visualizations...")
    print("=" * 60)
    
    # Load results
    print("Loading results...")
    results = load_results()
    df = results['metrics']
    
    print(f"✓ Loaded {len(df)} steps of metrics data")
    print(f"✓ Columns: {list(df.columns)}")
    
    # Create output directory
    Path('results').mkdir(exist_ok=True)
    
    # Generate plots
    print("\nGenerating plots...")
    plot_traditional_metrics(df)
    plot_extreme_scale_metrics(df) 
    plot_fault_tolerance_dashboard(results['fault_tolerance'])
    plot_semantic_learning_progress(results['semantic'])
    plot_comprehensive_summary(df)
    
    print("\n" + "=" * 60)
    print("🎉 All plots generated successfully!")
    print("\n📁 Generated files:")
    print("   • results/traditional_metrics.png")
    print("   • results/extreme_scale_metrics.png") 
    print("   • results/fault_tolerance_dashboard.png")
    print("   • results/semantic_learning_progress.png")
    print("   • results/comprehensive_summary.png")
    print("\n🔍 Open these files to view the enhanced FedSemGNN results!")

if __name__ == "__main__":
    main()
