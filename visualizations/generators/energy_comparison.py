#!/usr/bin/env python3
"""
Energy Comparison Generator
Creates individual energy comparison chart - saves to System Diagrams at 500 DPI
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

def create_energy_comparison():
    """Individual energy comparison chart"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    methods = ['FlatFedPPO', 'HierFedPPO', 'HSQF Heur.', 'RandomPlacement', 'FedSemGNN\n(Ours)']
    energy = [3.2, 2.8, 4.1, 3.5, 1.2]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#2E8B57']
    
    bars = ax.bar(methods, energy, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Federated Learning Energy Consumption (J/operation)', fontsize=14, fontweight='bold')
    ax.set_title('System-Wide Energy per Federated Learning Operation\nEdge Computing Infrastructure (50K+ Nodes)', fontsize=16, fontweight='bold')
    ax.set_ylim(0, 4.5)
    
    # Add metric specification
    ax.text(0.02, 0.98, 'Metric: Total energy consumption for federated model training cycle\n(includes local training + aggregation + model distribution across all edge nodes)', 
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, val in zip(bars, energy):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08, 
                f'{val:.1f} J', ha='center', fontsize=12, fontweight='bold')
    
    # Add savings annotation
    savings = ((energy[0] - energy[4]) / energy[0]) * 100  # FlatFedPPO vs FedSemGNN
    ax.annotate(f'-{savings:.1f}%\nvs FlatFedPPO', 
                xy=(4, energy[4]), xytext=(3.2, 3.8),
                fontsize=11, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    
    # Add method descriptions at bottom
    plt.figtext(0.5, 0.02, 
               'Energy Measurement: System-wide federated learning energy consumption including computation and communication | '
               'Baseline Methods: FlatFedPPO (Non-hierarchical federated PPO) | HierFedPPO (Hierarchical federated PPO) | '
               'HSQF Heur. (HSQF heuristic method) | RandomPlacement (Random assignment) | FedSemGNN (Semantic-aware federated learning)',
               ha='center', fontsize=10, style='italic', wrap=True)
    
    plt.tight_layout(rect=[0, 0.08, 1, 0.95])
    return fig

def main():
    """Generate energy comparison diagram"""
    print("Generating Energy Comparison diagram...")
    print("=" * 50)
    
    try:
        fig = create_energy_comparison()
        save_figure(fig, "energy_comparison.png")
        plt.close(fig)
        print("=" * 50)
        print("Successfully generated energy_comparison.png in System Diagrams folder")
        print("Individual energy metric saved at 500 DPI with correct baseline strategy names")
    except Exception as e:
        print(f"Error generating energy_comparison.png: {e}")

if __name__ == "__main__":
    main()