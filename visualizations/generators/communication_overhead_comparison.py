#!/usr/bin/env python3
"""
Communication Overhead Comparison Generator
Creates individual communication overhead comparison chart - saves to System Diagrams at 500 DPI
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

# Global style settings
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.facecolor": "white", 
    "figure.facecolor": "white",
    "font.size": 12,
    "axes.titlesize": 16,
    "axes.labelsize": 14
})

def save_figure(fig, filename):
    """Save figure to System Diagrams folder at 500 DPI"""
    os.makedirs("System Diagrams", exist_ok=True)
    filepath = os.path.join("System Diagrams", filename)
    fig.savefig(filepath, dpi=500, bbox_inches="tight")
    print(f"Saved: {filepath}")

def create_communication_overhead_comparison():
    """Individual communication overhead comparison chart"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    methods = ['FlatFedPPO', 'HierFedPPO', 'HSQF Heur.', 'RandomPlacement', 'FedSemGNN\n(Ours)']
    overhead = [45, 38, 52, 48, 15]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#2E8B57']
    
    bars = ax.bar(methods, overhead, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Federated Aggregation Communication Overhead (%)', fontsize=14, fontweight='bold')
    ax.set_title('Inter-Cluster Model Synchronization Overhead\nFederated Learning System (50K+ Nodes)', fontsize=16, fontweight='bold')
    ax.set_ylim(0, 60)
    
    # Add metric specification
    ax.text(0.02, 0.98, 'Metric: Communication overhead for federated parameter aggregation\n(bandwidth used for model updates / total available bandwidth)', 
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.7))
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, val in zip(bars, overhead):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{val}%', ha='center', fontsize=12, fontweight='bold')
    
    # Add reduction annotation
    reduction = ((overhead[0] - overhead[4]) / overhead[0]) * 100  # FlatFedPPO vs FedSemGNN
    ax.annotate(f'-{reduction:.1f}%\nvs FlatFedPPO', 
                xy=(4, overhead[4]), xytext=(3.2, 50),
                fontsize=11, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    
    # Add method descriptions at bottom
    plt.figtext(0.5, 0.02, 
               'Communication Measurement: Federated learning model synchronization overhead across distributed edge clusters | '
               'Baseline Methods: FlatFedPPO (Non-hierarchical federated PPO) | HierFedPPO (Hierarchical federated PPO) | '
               'HSQF Heur. (HSQF heuristic method) | RandomPlacement (Random assignment) | FedSemGNN (Semantic-aware federated learning)',
               ha='center', fontsize=10, style='italic', wrap=True)
    
    plt.tight_layout(rect=[0, 0.08, 1, 0.95])
    return fig

def main():
    """Generate communication overhead comparison diagram"""
    print("Generating Communication Overhead Comparison diagram...")
    print("=" * 50)
    
    try:
        fig = create_communication_overhead_comparison()
        save_figure(fig, "communication_overhead_comparison.png")
        plt.close(fig)
        print("=" * 50)
        print("Successfully generated communication_overhead_comparison.png in System Diagrams folder")
        print("Individual communication overhead metric saved at 500 DPI with correct baseline strategy names")
    except Exception as e:
        print(f"Error generating communication_overhead_comparison.png: {e}")

if __name__ == "__main__":
    main()