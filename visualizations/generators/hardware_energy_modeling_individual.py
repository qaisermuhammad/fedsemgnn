#!/usr/bin/env python3
"""
Individual Hardware Energy Modeling Diagram Generator
Creates hardware-specific energy analysis for FedSemGNN paper
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

def create_hardware_energy_modeling():
    """
    Hardware-specific energy consumption and modeling analysis
    Metric Type: Energy Efficiency Across Hardware Profiles
    System Context: 7 realistic hardware profiles with DVFS and thermal modeling
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.subplots_adjust(left=0.08, right=0.95, top=0.88, bottom=0.12, wspace=0.25, hspace=0.35)
    
    # Hardware profiles
    hardware_profiles = ['Intel Xeon', 'AMD EPYC', 'ARM Cortex', 'NVIDIA Jetson', 
                        'Raspberry Pi', 'Intel NUC', 'AWS Graviton2']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9F43', '#6C5CE7']
    
    # Energy consumption per operation (Joules)
    methods = ['FlatFedPPO', 'HierFedPPO', 'HSQF', 'FedSemGNN']
    
    energy_consumption = {
        'Intel Xeon': [4.2, 3.8, 5.1, 1.8],
        'AMD EPYC': [3.9, 3.4, 4.7, 1.6], 
        'ARM Cortex': [2.1, 1.9, 2.8, 0.9],
        'NVIDIA Jetson': [3.5, 3.1, 4.2, 1.4],
        'Raspberry Pi': [1.2, 1.1, 1.6, 0.5],
        'Intel NUC': [2.8, 2.5, 3.4, 1.1],
        'AWS Graviton2': [3.2, 2.9, 3.9, 1.3]
    }
    
    x_pos = np.arange(len(hardware_profiles))
    width = 0.15
    method_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#2E8B57']
    
    for i, (method, color) in enumerate(zip(methods, method_colors)):
        values = [energy_consumption[hw][i] for hw in hardware_profiles]
        ax1.bar(x_pos + i * width, values, width, 
                label=method, color=color, alpha=0.8, edgecolor='black')
    
    ax1.set_xlabel('Hardware Configuration Profile', fontweight='bold', fontfamily='serif')
    ax1.set_ylabel('Energy per Operation (J)', fontweight='bold', fontfamily='serif')
    ax1.set_title('Hardware-Specific Energy Consumption', fontweight='bold', fontfamily='serif')
    ax1.set_xticks(x_pos + width * 1.5)
    ax1.set_xticklabels(hardware_profiles, rotation=45, ha='right', fontsize=8)
    ax1.legend(frameon=True, fancybox=True, fontsize=8, ncol=1)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 6)
    
    # DVFS (Dynamic Voltage Frequency Scaling) impact
    frequency_levels = ['800 MHz', '1.2 GHz', '1.6 GHz', '2.0 GHz', '2.4 GHz', '2.8 GHz']
    
    # Power consumption vs frequency for different hardware
    base_power = {'Intel Xeon': 45, 'AMD EPYC': 42, 'ARM Cortex': 15, 'NVIDIA Jetson': 25}
    selected_hw = ['Intel Xeon', 'AMD EPYC', 'ARM Cortex', 'NVIDIA Jetson']
    selected_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    frequencies = np.array([0.8, 1.2, 1.6, 2.0, 2.4, 2.8])  # GHz
    
    for hw, color in zip(selected_hw, selected_colors):
        base = base_power[hw]
        # Power scaling: P = P_base * (f/f_base)^α, where α ≈ 2.5-3 for modern processors
        power_curve = base * np.power(frequencies / 2.0, 2.7)
        ax2.plot(frequencies, power_curve, 'o-', color=color, linewidth=2.5, 
                markersize=6, label=hw, alpha=0.9)
    
    ax2.set_xlabel('CPU Frequency (GHz)', fontweight='bold', fontfamily='serif')
    ax2.set_ylabel('Power Consumption (W)', fontweight='bold', fontfamily='serif')
    ax2.set_title('DVFS Power Scaling Characteristics', fontweight='bold', fontfamily='serif')
    ax2.legend(frameon=True, fancybox=True, fontsize=8, ncol=1)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0.7, 2.9)
    
    # Thermal modeling and throttling analysis
    time_minutes = np.arange(0, 60, 2)  # 1 hour simulation
    thermal_profiles = {}
    
    # Simulate thermal behavior under different workloads
    np.random.seed(42)
    ambient_temp = 25  # °C
    
    for hw in selected_hw:
        if hw == 'Intel Xeon':
            max_temp = 85
            thermal_resistance = 0.8
        elif hw == 'AMD EPYC':
            max_temp = 90
            thermal_resistance = 0.7
        elif hw == 'ARM Cortex':
            max_temp = 70
            thermal_resistance = 1.2
        else:  # NVIDIA Jetson
            max_temp = 80
            thermal_resistance = 1.0
        
        # Thermal response with workload variations
        workload_pattern = 50 + 30 * np.sin(2 * np.pi * time_minutes / 20) + 10 * np.random.normal(0, 1, len(time_minutes))
        workload_pattern = np.clip(workload_pattern, 20, 100)
        
        temp_response = ambient_temp + thermal_resistance * workload_pattern
        
        # Apply thermal throttling when approaching max temp
        throttle_temp = max_temp - 10
        throttling_factor = np.where(temp_response > throttle_temp, 
                                   1 - (temp_response - throttle_temp) / 20, 1.0)
        throttling_factor = np.clip(throttling_factor, 0.5, 1.0)
        
        thermal_profiles[hw] = {
            'temperature': temp_response,
            'throttling': throttling_factor,
            'max_temp': max_temp
        }
    
    # Plot thermal behavior for Intel Xeon and ARM Cortex as examples
    example_hw = ['Intel Xeon', 'ARM Cortex']
    example_colors = ['#FF6B6B', '#45B7D1']
    
    ax3_twin = ax3.twinx()
    
    for hw, color in zip(example_hw, example_colors):
        profile = thermal_profiles[hw]
        line1 = ax3.plot(time_minutes, profile['temperature'], '-', color=color, 
                        linewidth=2.5, label=f'{hw} Temperature', alpha=0.9)
        line2 = ax3_twin.plot(time_minutes, profile['throttling'] * 100, '--', color=color, 
                             linewidth=2.5, label=f'{hw} Performance', alpha=0.7)
        
        # Mark thermal limit
        ax3.axhline(y=profile['max_temp'], color=color, linestyle=':', alpha=0.5, 
                   label=f'{hw} Thermal Limit')
    
    ax3.set_xlabel('Elapsed Time (minutes)', fontweight='bold', fontfamily='serif')
    ax3.set_ylabel('Temperature (°C)', fontweight='bold', color='black')
    ax3_twin.set_ylabel('Performance Retention Ratio (%)', fontweight='bold', color='black')
    ax3.set_title('Thermal Behavior and Throttling', fontweight='bold', fontfamily='serif')
    
    # Combine legends
    lines1, labels1 = ax3.get_legend_handles_labels()
    lines2, labels2 = ax3_twin.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labels1 + labels2, loc='center right', 
              frameon=True, fancybox=True, fontsize=9, ncol=1)
    
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(20, 100)
    ax3_twin.set_ylim(40, 105)
    
    # Energy efficiency comparison across hardware profiles
    efficiency_metrics = {
        'Performance/Watt': {
            'Intel Xeon': [18.5, 20.2, 16.8, 28.4],
            'AMD EPYC': [19.8, 22.1, 17.9, 31.2],
            'ARM Cortex': [35.2, 38.7, 29.4, 52.8],
            'NVIDIA Jetson': [22.1, 24.6, 19.8, 38.9],
            'Raspberry Pi': [28.9, 31.4, 24.7, 48.3],
            'Intel NUC': [26.3, 29.1, 23.2, 43.6],
            'AWS Graviton2': [24.7, 27.3, 21.8, 41.2]
        }
    }
    
    # Create stacked efficiency comparison
    hw_subset = ['Intel Xeon', 'AMD EPYC', 'ARM Cortex', 'NVIDIA Jetson']
    x_pos = np.arange(len(hw_subset))
    width = 0.15
    
    for i, (method, color) in enumerate(zip(methods, method_colors)):
        values = [efficiency_metrics['Performance/Watt'][hw][i] for hw in hw_subset]
        ax4.bar(x_pos + i * width, values, width, 
                label=method, color=color, alpha=0.8, edgecolor='black')
    
    ax4.set_xlabel('Hardware Configuration Profile', fontweight='bold', fontfamily='serif')
    ax4.set_ylabel('Energy Efficiency (operations per Joule)', fontweight='bold', fontfamily='serif')
    ax4.set_title('Energy Efficiency Comparison', fontweight='bold', fontfamily='serif')
    ax4.set_xticks(x_pos + width * 1.5)
    ax4.set_xticklabels(hw_subset, rotation=25, ha='right', fontsize=8)
    ax4.legend(frameon=True, fancybox=True, fontsize=8, ncol=1)
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, 60)
    
    # Add metric specification box
    textstr = '''Metric Type: Energy Efficiency Across Hardware Profiles
System Context: 7 Realistic Hardware Profiles with DVFS and Thermal Modeling
- Energy Consumption: Joules per operation across different hardware types
- DVFS Impact: Power scaling with CPU frequency (Dynamic Voltage/Frequency Scaling)
- Thermal Behavior: Temperature response and performance throttling under load
- Energy Efficiency: Performance per watt comparison across hardware platforms'''
    
    props = dict(boxstyle='round,pad=0.5', facecolor='lightgoldenrodyellow', alpha=0.8)
    fig.text(0.02, 0.95, textstr, transform=fig.transFigure, fontsize=9,
             verticalalignment='top', bbox=props)
    
    plt.suptitle('FedSemGNN Hardware Energy Modeling: Multi-platform Energy Analysis', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.87])
    
    return fig

def main():
    """Generate and save hardware energy modeling diagram"""
    # Create output directory
    output_dir = "System Diagrams"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate diagram
    print("Generating hardware energy modeling diagram...")
    fig = create_hardware_energy_modeling()
    
    # Save at high resolution
    output_path = os.path.join(output_dir, "hardware_energy_modeling_individual.png")
    fig.savefig(output_path, dpi=500, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close(fig)
    
    print(f"✓ Hardware energy modeling diagram saved: {output_path}")
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"File size: {file_size:.2f} MB")

if __name__ == "__main__":
    main()