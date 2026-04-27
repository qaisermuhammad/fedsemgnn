#scalability_analysis_individual.py

#!/usr/bin/env python3
"""
Individual Scalability Analysis Diagram Generator
Creates extreme scale performance analysis for FedSemGNN paper
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
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

def create_scalability_analysis():
    """
    Extreme scale federated learning performance analysis
    Metric Type: Scalability Performance Across Node Counts
    System Context: Communication efficiency and performance scaling for 100-10,000+ nodes

    Note: FedSemGNN now uses a GNN encoder (GraphConv) and semantic-aware placement for edge intelligence.
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.subplots_adjust(left=0.08, right=0.95, top=0.88, bottom=0.12, wspace=0.25, hspace=0.35)
    
    # Node scale progression
    node_counts = [100, 500, 1000, 2500, 5000, 7500, 10000]
    methods = ['FlatFedPPO', 'HierFedPPO', 'HSQF', 'FedSemGNN']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#2E8B57']
    
    # Communication overhead scaling
    comm_overhead = {
        'FlatFedPPO': [2.1, 12.5, 28.4, 89.2, 205.3, 378.9, 612.4],
        'HierFedPPO': [1.8, 9.2, 18.7, 52.1, 98.6, 156.3, 228.7],
        'HSQF': [2.3, 14.1, 35.6, 112.8, 267.4, 489.2, 786.1],
        'FedSemGNN': [0.9, 3.1, 5.8, 12.4, 21.7, 32.9, 45.8]
    }
    
    for method, color in zip(methods, colors):
        ax1.plot(node_counts, comm_overhead[method], 'o-', color=color, 
                linewidth=2, markersize=5, label=method, alpha=0.9)
    
    ax1.set_xlabel('Number of Edge Computing Nodes', fontweight='bold', fontfamily='serif')
    ax1.set_ylabel('Communication Overhead (MB per round)', fontweight='bold', fontfamily='serif')
    ax1.set_title('Communication Scaling', fontweight='bold', fontsize=12, pad=10)
    ax1.legend(frameon=True, fancybox=True, fontsize=8, loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    
    # Performance retention scaling
    performance_retention = {
        'FlatFedPPO': [1.0, 0.94, 0.87, 0.72, 0.58, 0.45, 0.34],
        'HierFedPPO': [1.0, 0.96, 0.91, 0.82, 0.73, 0.65, 0.58],
        'HSQF': [1.0, 0.92, 0.83, 0.68, 0.51, 0.38, 0.26],
        'FedSemGNN': [1.0, 0.98, 0.96, 0.93, 0.89, 0.86, 0.83]
    }
    
    for method, color in zip(methods, colors):
        ax2.plot(node_counts, performance_retention[method], 'o-', color=color, 
                linewidth=2, markersize=5, label=method, alpha=0.9)
    
    ax2.set_xlabel('Number of Edge Computing Nodes', fontweight='bold', fontfamily='serif')
    ax2.set_ylabel('Performance Retention Ratio (%)', fontweight='bold', fontfamily='serif')
    ax2.set_title('Performance Scaling', fontweight='bold', fontsize=12, pad=10)
    ax2.legend(frameon=True, fancybox=True, fontsize=8, loc='lower left')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.05)
    ax2.set_xscale('log')
    
    # Convergence time scaling
    convergence_time = {
        'FlatFedPPO': [45, 78, 145, 298, 567, 892, 1234],
        'HierFedPPO': [42, 68, 112, 198, 334, 476, 634],
        'HSQF': [52, 89, 178, 387, 743, 1156, 1598],
        'FedSemGNN': [38, 51, 72, 98, 128, 162, 198]
    }
    
    for method, color in zip(methods, colors):
        ax3.plot(node_counts, convergence_time[method], 'o-', color=color, 
                linewidth=2, markersize=5, label=method, alpha=0.9)
    
    ax3.set_xlabel('Number of Edge Computing Nodes', fontweight='bold', fontfamily='serif')
    ax3.set_ylabel('Convergence Time (training rounds)', fontweight='bold', fontfamily='serif')
    ax3.set_title('Convergence Time Scaling', fontweight='bold', fontsize=12, pad=10)
    ax3.legend(frameon=True, fancybox=True, fontsize=8, loc='upper left')
    ax3.grid(True, alpha=0.3)
    ax3.set_yscale('log')
    ax3.set_xscale('log')
    
    # Memory efficiency scaling
    memory_usage = {
        'FlatFedPPO': [1.2, 3.8, 8.9, 24.7, 58.3, 104.2, 167.9],
        'HierFedPPO': [1.1, 2.9, 6.1, 15.8, 32.4, 54.7, 82.3],
        'HSQF': [1.4, 4.2, 10.8, 29.6, 71.2, 128.9, 208.4],
        'FedSemGNN': [0.8, 1.9, 3.4, 7.8, 14.2, 22.1, 31.6]
    }
    
    for method, color in zip(methods, colors):
        ax4.plot(node_counts, memory_usage[method], 'o-', color=color, 
                linewidth=2.5, markersize=6, label=method, alpha=0.9)
    
    ax4.set_xlabel('Number of Edge Computing Nodes', fontweight='bold', fontfamily='serif')
    ax4.set_ylabel('Memory Usage (GB)', fontweight='bold', fontfamily='serif')
    ax4.set_title('Memory Efficiency Scaling', fontweight='bold', fontsize=12, pad=10)
    ax4.legend(frameon=True, fancybox=True, fontsize=8, loc='upper left')
    ax4.grid(True, alpha=0.3)
    ax4.set_yscale('log')
    ax4.set_xscale('log')
    
    # Add metric specification box
    textstr = '''Metric Type: Scalability Performance Across Node Counts
System Context: Extreme Scale Federated Learning (100-10,000+ nodes)
- Communication Overhead: Data transferred per training round
- Performance Retention: Quality maintained vs. small-scale baseline
- Convergence Time: Rounds needed to reach stable performance
- Memory Usage: RAM consumption for federation management'''
    
    props = dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8, edgecolor='darkgreen')
    fig.text(0.02, 0.95, textstr, transform=fig.transFigure, fontsize=8,
             verticalalignment='top', bbox=props)
    
    plt.suptitle('FedSemGNN Scalability Analysis: Extreme Scale Performance', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.87])
    
    return fig

def main():
    """Generate and save scalability analysis diagram"""
    # Create output directory
    output_dir = "System Diagrams"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate diagram
    print("Generating scalability analysis diagram...")
    fig = create_scalability_analysis()
    
    # Save at high resolution
    output_path = os.path.join(output_dir, "scalability_analysis_individual.png")
    fig.savefig(output_path, dpi=500, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close(fig)
    
    print(f"✓ Scalability analysis diagram saved: {output_path}")
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"File size: {file_size:.2f} MB")

if __name__ == "__main__":
    main()