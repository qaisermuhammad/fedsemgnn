#performance_comparison.py
#!/usr/bin/env python3
"""
Separate Performance Comparison Generator  
Creates performance comparison chart with correct baseline strategy names - saves to System Diagrams at 500 DPI
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

def create_performance_comparison():
    """Performance comparison chart with correct baseline strategy names"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Performance Comparison: FedSemGNN vs State-of-the-Art Baselines\n(50K+ Node Infrastructure)', fontsize=16, fontweight='bold')
    
    methods = ['FlatFedPPO', 'HierFedPPO', 'HSQF Heur.', 'RandomPlacement', 'FedSemGNN\n(Ours)']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#2E8B57']
    
    # Accuracy
    ax = axes[0, 0]
    accuracy = [88.5, 85.2, 82.7, 65.3, 96.1]
    bars = ax.bar(methods, accuracy, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax.set_title('Placement Accuracy (%)', fontweight='bold', fontsize=12)
    ax.set_ylim(60, 100)
    ax.grid(True, alpha=0.3)
    for bar, val in zip(bars, accuracy):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold')
    
    # Latency
    ax = axes[0, 1]
    latency = [85, 79, 112, 95, 51]
    bars = ax.bar(methods, latency, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax.set_title('Average Latency (ms)', fontweight='bold', fontsize=12)
    ax.set_ylim(0, 120)
    ax.grid(True, alpha=0.3)
    for bar, val in zip(bars, latency):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{val} ms', ha='center', fontsize=10, fontweight='bold')
    
    # Energy
    ax = axes[1, 0]
    energy = [3.2, 2.8, 4.1, 3.5, 1.2]
    bars = ax.bar(methods, energy, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax.set_title('Energy per Operation (J)', fontweight='bold', fontsize=12)
    ax.set_ylim(0, 4.5)
    ax.grid(True, alpha=0.3)
    for bar, val in zip(bars, energy):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08, 
                f'{val:.1f} J', ha='center', fontsize=10, fontweight='bold')
    
    # Communication overhead
    ax = axes[1, 1]
    overhead = [45, 38, 52, 48, 15]
    bars = ax.bar(methods, overhead, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax.set_title('Communication Overhead (%)', fontweight='bold', fontsize=12)
    ax.set_ylim(0, 60)
    ax.grid(True, alpha=0.3)
    for bar, val in zip(bars, overhead):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{val}%', ha='center', fontsize=10, fontweight='bold')
    
    # Add method descriptions at bottom
    plt.figtext(0.5, 0.02, 
               'Baseline Methods: FlatFedPPO (Non-hierarchical federated PPO) | HierFedPPO (Hierarchical federated PPO) | '
               'HSQF Heur. (HSQF heuristic method) | RandomPlacement (Random assignment baseline) | FedSemGNN (Our proposed method)',
               ha='center', fontsize=10, style='italic', wrap=True)
    
    plt.tight_layout(rect=[0, 0.06, 1, 0.96])
    return fig

def main():
    """Generate performance_comparison diagram"""
    print("Generating Performance Comparison diagram...")
    print("=" * 50)
    
    try:
        fig = create_performance_comparison()
        save_figure(fig, "performance_comparison.png")
        plt.close(fig)  # Free memory
        print("=" * 50)
        print("Successfully generated performance_comparison.png in System Diagrams folder")
        print("Diagram saved at 500 DPI with correct baseline strategy names")
    except Exception as e:
        print(f"Error generating performance_comparison.png: {e}")

if __name__ == "__main__":
    main()