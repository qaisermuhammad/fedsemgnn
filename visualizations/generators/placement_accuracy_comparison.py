#placement_accuracy_comparison.py
#!/usr/bin/env python3
"""
Placement Accuracy Comparison Generator
Creates individual placement accuracy comparison chart - saves to System Diagrams at 500 DPI
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

def create_placement_accuracy_comparison():
    """Individual placement accuracy comparison chart"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    methods = ['FlatFedPPO', 'HierFedPPO', 'HSQF Heur.', 'RandomPlacement', 'FedSemGNN\n(Ours)']
    accuracy = [88.5, 85.2, 82.7, 65.3, 96.1]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#2E8B57']
    
    bars = ax.bar(methods, accuracy, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Service Placement Accuracy (%)', fontsize=14, fontweight='bold')
    ax.set_title('End-to-End Service Placement Accuracy\nFederated Edge Computing System (50K+ Nodes)', fontsize=16, fontweight='bold')
    ax.set_ylim(60, 100)
    
    # Add metric specification
    ax.text(0.02, 0.98, 'Metric: Successful QoS-aware service placements / Total placement requests', 
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, val in zip(bars, accuracy):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val:.1f}%', ha='center', fontsize=12, fontweight='bold')
    
    # Add improvement annotation
    improvement = accuracy[4] - accuracy[0]  # FedSemGNN vs FlatFedPPO
    ax.annotate(f'+{improvement:.1f}%\nvs FlatFedPPO', 
                xy=(4, accuracy[4]), xytext=(3.2, 92),
                fontsize=11, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    
    # Add method descriptions at bottom
    plt.figtext(0.5, 0.02, 
               'Service Placement Context: Real-time edge computing workload assignment with QoS constraints | '
               'Baseline Methods: FlatFedPPO (Non-hierarchical federated PPO) | HierFedPPO (Hierarchical federated PPO) | '
               'HSQF Heur. (HSQF heuristic method) | RandomPlacement (Random assignment) | FedSemGNN (Semantic-aware federated learning)',
               ha='center', fontsize=10, style='italic', wrap=True)
    
    plt.tight_layout(rect=[0, 0.08, 1, 0.95])
    return fig

def main():
    """Generate placement accuracy comparison diagram"""
    print("Generating Placement Accuracy Comparison diagram...")
    print("=" * 50)
    
    try:
        fig = create_placement_accuracy_comparison()
        save_figure(fig, "placement_accuracy_comparison.png")
        plt.close(fig)
        print("=" * 50)
        print("Successfully generated placement_accuracy_comparison.png in System Diagrams folder")
        print("Individual accuracy metric saved at 500 DPI with correct baseline strategy names")
    except Exception as e:
        print(f"Error generating placement_accuracy_comparison.png: {e}")

if __name__ == "__main__":
    main()