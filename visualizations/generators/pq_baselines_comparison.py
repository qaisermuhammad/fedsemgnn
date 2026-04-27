#pq_baselines_comparison.py

#!/usr/bin/env python3
"""
Separate PQ Baselines Comparison Generator
Creates comprehensive comparison with all baseline methods - saves to System Diagrams at 500 DPI
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
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12
})

def save_figure(fig, filename):
    """Save figure to System Diagrams folder at 500 DPI"""
    os.makedirs("System Diagrams", exist_ok=True)
    filepath = os.path.join("System Diagrams", filename)
    fig.savefig(filepath, dpi=500, bbox_inches="tight")
    print(f"Saved: {filepath}")

def create_pq_baselines_comparison():
    """Comprehensive comparison with all baseline methods"""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 10))
    
    # Placement Accuracy Comparison
    methods = ['FedSemGNN\n(Ours)', 'FlatFedPPO', 'HierFedPPO', 'HSQF Heur.', 'RandomPlacement']
    accuracy = [96.1, 88.5, 85.2, 82.7, 65.3]
    colors = ['#2E8B57', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    bars1 = ax1.bar(methods, accuracy, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('Service Placement Accuracy (%)', fontsize=12, fontweight='bold')
    ax1.set_title('QoS-Aware Service Placement Accuracy\n(Higher is Better)', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, 100)
    ax1.grid(True, alpha=0.3)
    
    # Add metric specification
    ax1.text(0.02, 0.98, 'QoS-constrained\nplacement success', 
            transform=ax1.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightblue", alpha=0.7))
    
    # Add value labels on bars
    for bar, val in zip(bars1, accuracy):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val}%', ha='center', va='bottom', fontweight='bold')
    
    # Add improvement annotations
    ax1.annotate(f'+{accuracy[0]-accuracy[1]:.1f}%', 
                xy=(0.5, (accuracy[0]+accuracy[1])/2), 
                xytext=(0.5, 92), fontsize=10, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green'))
    
    # Latency Comparison
    latency = [51, 85, 79, 112, 95]
    bars2 = ax2.bar(methods, latency, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('End-to-End Placement Latency (ms)', fontsize=12, fontweight='bold')
    ax2.set_title('Service Request to Decision Latency\n(Lower is Better)', fontsize=14, fontweight='bold')
    ax2.set_ylim(0, 130)
    ax2.grid(True, alpha=0.3)
    
    # Add metric specification
    ax2.text(0.02, 0.98, 'Request-to-placement\ndecision time', 
            transform=ax2.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightcoral", alpha=0.7))
    
    # Add value labels
    for bar, val in zip(bars2, latency):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{val}ms', ha='center', va='bottom', fontweight='bold')
    
    # Add reduction annotation
    reduction = ((latency[1]-latency[0])/latency[1])*100
    ax2.annotate(f'-{reduction:.1f}%', 
                xy=(0.5, (latency[0]+latency[1])/2),
                xytext=(0.5, 100), fontsize=10, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green'))
    
    # Energy Consumption
    energy = [1.2, 3.2, 2.8, 4.1, 3.5]
    bars3 = ax3.bar(methods, energy, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax3.set_ylabel('Federated Learning Energy (J/operation)', fontsize=12, fontweight='bold')
    ax3.set_title('System-Wide FL Training Energy\n(Lower is Better)', fontsize=14, fontweight='bold')
    ax3.set_ylim(0, 5)
    ax3.grid(True, alpha=0.3)
    
    # Add metric specification
    ax3.text(0.02, 0.98, 'Total FL cycle\nenergy consumption', 
            transform=ax3.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgreen", alpha=0.7))
    
    # Add value labels
    for bar, val in zip(bars3, energy):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{val}J', ha='center', va='bottom', fontweight='bold')
    
    # Add savings annotation
    savings = ((energy[1]-energy[0])/energy[1])*100
    ax3.annotate(f'-{savings:.1f}%', 
                xy=(0.5, (energy[0]+energy[1])/2),
                xytext=(0.5, 3.8), fontsize=10, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green'))
    
    # Add method descriptions at bottom
    plt.figtext(0.5, 0.02, 
               'System Context: Real-time federated edge computing with 50K+ nodes | Performance Metrics: QoS-aware placement accuracy, end-to-end latency, federated learning energy | '
               'Method Details: FedSemGNN (Semantic-aware federated learning with GCN) | FlatFedPPO (Non-hierarchical federated PPO) | '
               'HierFedPPO (Hierarchical federated PPO) | HSQF Heur. (HSQF heuristic baseline) | RandomPlacement (Random assignment baseline)',
               ha='center', fontsize=10, style='italic', wrap=True)
    
    plt.suptitle('FedSemGNN vs. State-of-the-Art Baseline Methods\nComprehensive Performance Analysis (50K+ Nodes)', 
                 fontsize=16, fontweight='bold', y=0.95)
    plt.tight_layout(rect=[0, 0.08, 1, 0.92])
    
    return fig

def main():
    """Generate pq_baselines_comparison diagram"""
    print("Generating PQ Baselines Comparison diagram...")
    print("=" * 50)
    
    try:
        fig = create_pq_baselines_comparison()
        save_figure(fig, "pq_baselines_comparison.png")
        plt.close(fig)  # Free memory
        print("=" * 50)
        print("Successfully generated pq_baselines_comparison.png in System Diagrams folder")
        print("Diagram saved at 500 DPI with correct baseline strategy names")
    except Exception as e:
        print(f"Error generating pq_baselines_comparison.png: {e}")

if __name__ == "__main__":
    main()