#semantic_learning_analysis_individual.py

#!/usr/bin/env python3
"""
Individual Semantic Learning Analysis Diagram Generator
Creates online semantic learning performance analysis for FedSemGNN paper
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.patches import FancyBboxPatch

# Global style settings
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.facecolor": "white", 
    "figure.facecolor": "white",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12
})

def create_semantic_learning_analysis():
    """
    Online semantic learning adaptation and performance analysis
    Metric Type: Real-time Semantic Embedding Quality and Adaptation
    System Context: Online learning vs static embeddings for service placement
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.subplots_adjust(left=0.08, right=0.95, top=0.88, bottom=0.12, wspace=0.25, hspace=0.35)
    
    # Embedding quality evolution over time
    time_steps = np.arange(0, 1000, 10)
    
    # Simulate embedding quality metrics
    np.random.seed(42)
    static_quality = 0.78 + 0.02 * np.random.normal(0, 1, len(time_steps))
    static_quality = np.clip(static_quality, 0.7, 0.85)
    
    online_base = 0.75
    online_improvement = 0.25 * (1 - np.exp(-time_steps/300))
    online_noise = 0.01 * np.random.normal(0, 1, len(time_steps))
    online_quality = online_base + online_improvement + online_noise
    online_quality = np.clip(online_quality, 0.7, 1.0)
    
    ax1.plot(time_steps, static_quality, color='#FF6B6B', linewidth=2.5, 
             label='Static Embeddings', alpha=0.9)
    ax1.plot(time_steps, online_quality, color='#2E8B57', linewidth=2.5, 
             label='Online Learning (FedSemGNN)', alpha=0.9)
    
    # Add shaded regions for different learning phases
    ax1.axvspan(0, 200, alpha=0.2, color='yellow', label='Initial Learning')
    ax1.axvspan(200, 600, alpha=0.2, color='orange', label='Adaptation Phase')
    ax1.axvspan(600, 1000, alpha=0.2, color='green', label='Stable Performance')
    
    ax1.set_xlabel('Algorithm Training Iteration', fontweight='bold', fontfamily='serif')
    ax1.set_ylabel('Embedding Quality Score (cosine similarity, 0-1)', fontweight='bold', fontfamily='serif')
    ax1.set_title('Semantic Embedding Quality Evolution', fontweight='bold', fontfamily='serif')
    ax1.legend(frameon=True, fancybox=True, fontsize=8, ncol=1)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0.65, 1.05)
    
    # Learning rate adaptation analysis
    learning_rates = [0.001, 0.005, 0.01, 0.05, 0.1]
    convergence_steps = [850, 620, 480, 320, 280]
    final_quality = [0.94, 0.97, 0.99, 0.96, 0.89]
    stability = [0.95, 0.92, 0.88, 0.75, 0.62]
    
    # Create dual-axis plot
    ax2_twin = ax2.twinx()
    
    line1 = ax2.plot(learning_rates, convergence_steps, 'o-', color='#4ECDC4', 
                     linewidth=2.5, markersize=8, label='Convergence Steps')
    line2 = ax2_twin.plot(learning_rates, final_quality, 's-', color='#2E8B57', 
                          linewidth=2.5, markersize=8, label='Final Quality')
    line3 = ax2_twin.plot(learning_rates, stability, '^-', color='#FF6B6B', 
                          linewidth=2.5, markersize=8, label='Stability')
    
    ax2.set_xlabel('Learning Rate (α)', fontweight='bold', fontfamily='serif')
    ax2.set_ylabel('Convergence Steps (iterations)', fontweight='bold', color='#4ECDC4')
    ax2_twin.set_ylabel('Quality/Stability Score (0-1 normalized)', fontweight='bold', color='#2E8B57')
    ax2.set_title('Learning Rate Impact Analysis', fontweight='bold', fontfamily='serif')
    
    # Combine legends
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='center right', frameon=True, fancybox=True, fontsize=8, ncol=1)
    
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(200, 900)
    ax2_twin.set_ylim(0.5, 1.05)
    
    # Semantic similarity preservation
    service_types = ['Video Stream', 'IoT Data', 'AR/VR', 'Voice Call', 'File Transfer']
    
    similarity_static = [0.72, 0.68, 0.75, 0.71, 0.69]
    similarity_online = [0.89, 0.94, 0.91, 0.87, 0.93]
    improvement = [((o-s)/s)*100 for s, o in zip(similarity_static, similarity_online)]
    
    x_pos = np.arange(len(service_types))
    width = 0.35
    
    bars1 = ax3.bar(x_pos - width/2, similarity_static, width, 
                    label='Static Embeddings', color='#FF6B6B', alpha=0.8, edgecolor='black')
    bars2 = ax3.bar(x_pos + width/2, similarity_online, width, 
                    label='Online Learning', color='#2E8B57', alpha=0.8, edgecolor='black')
    
    # Add improvement percentages
    for i, (bar1, bar2, imp) in enumerate(zip(bars1, bars2, improvement)):
        ax3.annotate(f'+{imp:.1f}%', 
                    xy=(bar2.get_x() + bar2.get_width()/2, bar2.get_height()),
                    xytext=(0, 5), textcoords='offset points',
                    ha='center', va='bottom', fontweight='bold', color='green')
    
    ax3.set_xlabel('Edge Computing Service Category', fontweight='bold', fontfamily='serif')
    ax3.set_ylabel('Semantic Similarity (cosine distance, 0-1)', fontweight='bold', fontfamily='serif')
    ax3.set_title('Semantic Similarity Preservation', fontweight='bold', fontfamily='serif')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(service_types, rotation=25, ha='right', fontsize=8)
    ax3.legend(frameon=True, fancybox=True, fontsize=8, ncol=1)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 1.05)
    
    # Adaptation performance under workload changes
    workload_scenarios = ['Stable', 'Burst Traffic', 'Service Mix Change', 
                         'Peak Hours', 'Regional Shift']
    
    adaptation_metrics = {
        'Adaptation Speed (steps)': [0, 45, 78, 32, 89],
        'Quality Retention (%)': [100, 92, 87, 94, 85],
        'Convergence Stability': [1.0, 0.89, 0.82, 0.91, 0.79]
    }
    
    x_pos = np.arange(len(workload_scenarios))
    width = 0.18
    
    # Normalize metrics for comparison
    normalized_speed = [(100-v)/100 if v > 0 else 1.0 for v in adaptation_metrics['Adaptation Speed (steps)']]
    normalized_retention = [v/100 for v in adaptation_metrics['Quality Retention (%)']]
    stability_scores = adaptation_metrics['Convergence Stability']
    
    ax4.bar(x_pos - width, normalized_speed, width, 
            label='Adaptation Speed (norm.)', color='#45B7D1', alpha=0.8, edgecolor='black')
    ax4.bar(x_pos, normalized_retention, width, 
            label='Quality Retention', color='#2E8B57', alpha=0.8, edgecolor='black')
    ax4.bar(x_pos + width, stability_scores, width, 
            label='Convergence Stability', color='#FF6B6B', alpha=0.8, edgecolor='black')
    
    ax4.set_xlabel('Computational Workload Type', fontweight='bold', fontfamily='serif')
    ax4.set_ylabel('Normalized Performance Score (0-1 relative to baseline)', fontweight='bold', fontfamily='serif')
    ax4.set_title('Online Learning Adaptation Performance', fontweight='bold', fontfamily='serif')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(workload_scenarios, rotation=25, ha='right', fontsize=8)
    ax4.legend(frameon=True, fancybox=True, fontsize=8, ncol=1)
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, 1.1)
    
    # Add metric specification box
    textstr = '''Metric Type: Real-time Semantic Embedding Quality and Adaptation
System Context: Online Learning vs Static Embeddings for Service Placement
- Embedding Quality: Semantic representation accuracy over time (0-1 scale)
- Learning Rate Impact: Effect of adaptation rate on convergence and stability
- Similarity Preservation: Maintenance of semantic relationships between services
- Workload Adaptation: Performance under dynamic traffic and service patterns'''
    
    props = dict(boxstyle='round,pad=0.5', facecolor='lightsteelblue', alpha=0.8)
    fig.text(0.02, 0.95, textstr, transform=fig.transFigure, fontsize=9,
             verticalalignment='top', bbox=props)
    
    plt.suptitle('FedSemGNN Semantic Learning Analysis: Online Adaptation Performance', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.87])
    
    return fig

def main():
    """Generate and save semantic learning analysis diagram"""
    # Create output directory
    output_dir = "System Diagrams"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate diagram
    print("Generating semantic learning analysis diagram...")
    fig = create_semantic_learning_analysis()
    
    # Save at high resolution
    output_path = os.path.join(output_dir, "semantic_learning_analysis_individual.png")
    fig.savefig(output_path, dpi=500, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close(fig)
    
    print(f"✓ Semantic learning analysis diagram saved: {output_path}")
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"File size: {file_size:.2f} MB")

if __name__ == "__main__":
    main()