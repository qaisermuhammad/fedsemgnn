#latency_comparison.py

#!/usr/bin/env python3
"""
Latency Comparison Generator
Creates individual latency comparison chart - saves to System Diagrams at 500 DPI
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

def create_latency_comparison():
    """Individual latency comparison chart"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    methods = ['FlatFedPPO', 'HierFedPPO', 'HSQF Heur.', 'RandomPlacement', 'FedSemGNN\n(Ours)']
    latency = [85, 79, 112, 95, 51]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#2E8B57']
    
    bars = ax.bar(methods, latency, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('End-to-End Service Placement Latency (ms)', fontsize=14, fontweight='bold')
    ax.set_title('Service Request to Placement Decision Latency\nFederated Edge Computing System (50K+ Nodes)', fontsize=16, fontweight='bold')
    ax.set_ylim(0, 120)
    
    # Add metric specification
    ax.text(0.02, 0.98, 'Metric: Time from service request arrival to placement decision completion\n(includes semantic processing + GCN inference + PPO decision)', 
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, val in zip(bars, latency):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{val} ms', ha='center', fontsize=12, fontweight='bold')
    
    # Add reduction annotation
    reduction = ((latency[0] - latency[4]) / latency[0]) * 100  # FlatFedPPO vs FedSemGNN
    ax.annotate(f'-{reduction:.1f}%\nvs FlatFedPPO', 
                xy=(4, latency[4]), xytext=(3.2, 100),
                fontsize=11, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    
    # Add method descriptions at bottom
    plt.figtext(0.5, 0.02, 
               'Latency Measurement: Real-time edge service placement pipeline from request to decision | '
               'Baseline Methods: FlatFedPPO (Non-hierarchical federated PPO) | HierFedPPO (Hierarchical federated PPO) | '
               'HSQF Heur. (HSQF heuristic method) | RandomPlacement (Random assignment) | FedSemGNN (Semantic-aware federated learning)',
               ha='center', fontsize=10, style='italic', wrap=True)
    
    plt.tight_layout(rect=[0, 0.08, 1, 0.95])
    return fig

def main():
    """Generate latency comparison diagram"""
    print("Generating Latency Comparison diagram...")
    print("=" * 50)
    
    try:
        fig = create_latency_comparison()
        save_figure(fig, "latency_comparison.png")
        plt.close(fig)
        print("=" * 50)
        print("Successfully generated latency_comparison.png in System Diagrams folder")
        print("Individual latency metric saved at 500 DPI with correct baseline strategy names")
    except Exception as e:
        print(f"Error generating latency_comparison.png: {e}")

if __name__ == "__main__":
    main()