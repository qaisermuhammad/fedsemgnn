#!/usr/bin/env python3
"""
6G Edge Server Power Consumption Model
Provides realistic power consumption calculations for 6G edge computing infrastructure
"""

import math
import numpy as np
from typing import Dict, Any, Optional, List
import json
import os

class EdgeServerPowerModel:
    """
    Realistic 6G edge server power consumption model based on infrastructure scaling
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the 6G edge server power model"""
        
        # Default 6G edge server configuration
        self.config = config or {
            "edge_server_specs": {
                "base_power_per_server_w": 15.0,     # Small edge server base power (Watts)
                "network_overhead_w": 5.0,           # Network coordination overhead per server
                "cooling_efficiency_pue": 1.3,       # Power Usage Effectiveness for cooling
                "idle_power_ratio": 0.3,             # Idle power as fraction of base power
                "max_power_multiplier": 2.5          # Maximum power under full load
            },
            "algorithm_complexity": {
                # REALISTIC MODE: Reflects actual computational complexity differences
                "realistic": {
                    "FedSemGNN": 1.2,        # Graph Neural Network processing overhead
                    "FlatFedPPO": 3.5,       # Complex PPO reinforcement learning  
                    "HierFedPPO": 2.8,       # Hierarchical PPO processing
                    "HSQF": 2.2,             # Moderate complexity scheduling
                    "RandomPlacement": 1.0,  # Baseline minimal processing
                    "Flatfedppo": 3.5,       # Alias for backward compatibility
                    "Hierfedppo": 2.8,       # Alias for backward compatibility
                    "Hsqf": 2.2,             # Alias for backward compatibility
                    "Randomplace": 1.0,      # Alias for backward compatibility
                    "default": 1.5           # Default for unknown algorithms
                },
                # FAIR COMPARISON MODE: Equal computational complexity for pure algorithm evaluation
                "fair_comparison": {
                    "FedSemGNN": 1.0,        # Equal baseline for fair comparison
                    "FlatFedPPO": 1.0,       # Equal baseline for fair comparison
                    "HierFedPPO": 1.0,       # Equal baseline for fair comparison
                    "HSQF": 1.0,             # Equal baseline for fair comparison
                    "RandomPlacement": 1.0,  # Equal baseline for fair comparison
                    "Flatfedppo": 1.0,       # Alias for backward compatibility
                    "Hierfedppo": 1.0,       # Alias for backward compatibility
                    "Hsqf": 1.0,             # Alias for backward compatibility
                    "Randomplace": 1.0,      # Alias for backward compatibility
                    "default": 1.0           # Equal baseline for fair comparison
                },
                "mode": "realistic"          # Current mode: "realistic" or "fair_comparison"
            },
            "central_server": {
                "base_power_w": 500.0,   # Central coordination server power
                "scaling_factor": 1.2    # How central server scales with algorithm complexity
            },
            "deployment_scenarios": {
                "smart_city": {"nodes": 10000, "server_type": "small"},
                "metropolitan": {"nodes": 100000, "server_type": "medium"},
                "national": {"nodes": 1000000, "server_type": "large"}
            }
        }
        
        # 6G research context parameters
        self.research_context = {
            "co2_emission_factor": 0.4,      # kg CO2 per kWh (global average)
            "electricity_cost": 0.10,        # USD per kWh
            "hours_per_year": 8760,          # For annual calculations
            "power_scaling_mode": "linear"    # How power scales with network size
        }
    
    def set_comparison_mode(self, mode: str) -> None:
        """
        Set the algorithm complexity comparison mode
        
        Args:
            mode: Either 'realistic' or 'fair_comparison'
                 - 'realistic': Uses actual computational complexity differences
                 - 'fair_comparison': Equal complexity for pure algorithm evaluation
        """
        if mode not in ["realistic", "fair_comparison"]:
            raise ValueError("Mode must be 'realistic' or 'fair_comparison'")
        
        self.config["algorithm_complexity"]["mode"] = mode
        
        # Set environment variable for algorithms to use
        import os
        os.environ['FEDSEMGNN_COMPARISON_MODE'] = mode
        
        print(f"[6G POWER MODEL] Switched to {mode.upper()} mode")
    
    def get_comparison_mode(self) -> str:
        """Get the current comparison mode"""
        return self.config["algorithm_complexity"]["mode"]
    
    def calculate_edge_server_power(self, algorithm: str, num_nodes: int, 
                                   load_factor: float = 0.7) -> Dict[str, float]:
        """
        Calculate realistic 6G edge server power consumption
        
        Args:
            algorithm: Algorithm name (e.g., 'FedSemGNN', 'Flatfedppo')
            num_nodes: Number of edge servers in the network
            load_factor: Server load factor (0.0 to 1.0)
        
        Returns:
            Dictionary with detailed power consumption breakdown
        """
        
        # Get algorithm complexity factor based on current mode
        complexity_mode = self.config["algorithm_complexity"]["mode"]
        complexity_dict = self.config["algorithm_complexity"][complexity_mode]
        complexity_factor = complexity_dict.get(
            algorithm, complexity_dict["default"]
        )
        
        # Edge server specifications
        edge_specs = self.config["edge_server_specs"]
        base_power = edge_specs["base_power_per_server_w"]
        network_overhead = edge_specs["network_overhead_w"]
        pue = edge_specs["cooling_efficiency_pue"]
        idle_ratio = edge_specs["idle_power_ratio"]
        max_multiplier = edge_specs["max_power_multiplier"]
        
        # Calculate power per edge server
        # Power varies between idle and maximum based on load
        idle_power = base_power * idle_ratio
        max_power = base_power * max_multiplier
        computational_power = idle_power + (max_power - idle_power) * load_factor
        
        # Apply algorithm complexity
        algorithm_power = computational_power * complexity_factor
        
        # Add network coordination overhead
        total_power_per_server = (algorithm_power + network_overhead) * pue
        
        # Total infrastructure power scales with number of edge servers
        total_infrastructure_power = total_power_per_server * num_nodes
        
        # Central server power
        central_specs = self.config["central_server"]
        central_base_power = central_specs["base_power_w"]
        central_scaling = central_specs["scaling_factor"]
        central_server_power = central_base_power * (complexity_factor ** central_scaling)
        
        # Total system power
        total_system_power = total_infrastructure_power + central_server_power
        
        return {
            "power_per_edge_server_w": total_power_per_server,
            "total_infrastructure_power_w": total_infrastructure_power,
            "central_server_power_w": central_server_power,
            "total_system_power_w": total_system_power,
            "power_per_node_mw": (total_system_power / num_nodes) * 1000,
            "complexity_factor": complexity_factor,
            "load_factor": load_factor,
            "algorithm": algorithm,
            "num_nodes": num_nodes
        }
    
    def calculate_6g_research_metrics(self, power_breakdown: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate 6G research-relevant metrics from power consumption
        
        Args:
            power_breakdown: Result from calculate_edge_server_power()
        
        Returns:
            Dictionary with research metrics
        """
        
        total_power_kw = power_breakdown["total_system_power_w"] / 1000
        
        # Annual metrics
        annual_energy_kwh = total_power_kw * self.research_context["hours_per_year"]
        annual_co2_kg = annual_energy_kwh * self.research_context["co2_emission_factor"]
        annual_cost_usd = annual_energy_kwh * self.research_context["electricity_cost"]
        
        # Efficiency metrics
        energy_efficiency_ops_per_watt = 1000 / power_breakdown["power_per_edge_server_w"]
        infrastructure_efficiency = power_breakdown["total_infrastructure_power_w"] / power_breakdown["total_system_power_w"]
        
        return {
            "annual_energy_consumption_kwh": annual_energy_kwh,
            "annual_co2_emissions_kg": annual_co2_kg,
            "annual_operational_cost_usd": annual_cost_usd,
            "energy_efficiency_ops_per_watt": energy_efficiency_ops_per_watt,
            "infrastructure_efficiency_ratio": infrastructure_efficiency,
            "power_density_w_per_km2": total_power_kw * 1000,  # Assuming 1 server per km2
            "deployment_scalability_class": self._classify_scalability(power_breakdown)
        }
    
    def _classify_scalability(self, power_breakdown: Dict[str, float]) -> str:
        """Classify algorithm scalability for 6G deployment"""
        
        power_per_node_mw = power_breakdown["power_per_node_mw"]
        
        if power_per_node_mw < 50:
            return "EXCELLENT"
        elif power_per_node_mw < 100:
            return "GOOD"
        elif power_per_node_mw < 200:
            return "MODERATE"
        else:
            return "POOR"
    
    def compare_algorithms(self, algorithms: List[str], num_nodes: int, 
                          load_factor: float = 0.7) -> Dict[str, Dict[str, float]]:
        """
        Compare multiple algorithms for 6G edge server deployment
        
        Args:
            algorithms: List of algorithm names
            num_nodes: Number of edge servers
            load_factor: Server load factor
        
        Returns:
            Dictionary with comparison results for each algorithm
        """
        
        comparison = {}
        
        for algorithm in algorithms:
            power_breakdown = self.calculate_edge_server_power(algorithm, num_nodes, load_factor)
            research_metrics = self.calculate_6g_research_metrics(power_breakdown)
            
            comparison[algorithm] = {
                **power_breakdown,
                **research_metrics
            }
        
        return comparison
    
    def generate_scaling_study(self, algorithm: str, node_counts: List[int], 
                              load_factor: float = 0.7) -> List[Dict[str, float]]:
        """
        Generate scaling study data for a specific algorithm
        
        Args:
            algorithm: Algorithm name
            node_counts: List of node counts to test
            load_factor: Server load factor
        
        Returns:
            List of power consumption data for each node count
        """
        
        scaling_data = []
        
        for num_nodes in node_counts:
            power_breakdown = self.calculate_edge_server_power(algorithm, num_nodes, load_factor)
            research_metrics = self.calculate_6g_research_metrics(power_breakdown)
            
            scaling_data.append({
                **power_breakdown,
                **research_metrics
            })
        
        return scaling_data
    
    def save_config(self, filename: str) -> None:
        """Save current configuration to file"""
        config_data = {
            "edge_server_power_model": self.config,
            "research_context": self.research_context
        }
        
        with open(filename, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def load_config(self, filename: str) -> None:
        """Load configuration from file"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self.config = data.get("edge_server_power_model", self.config)
                self.research_context = data.get("research_context", self.research_context)

# Convenience function for easy integration
def get_6g_edge_power(algorithm: str, num_nodes: int, load_factor: float = 0.7, 
                      comparison_mode: str = None) -> float:
    """
    Simple function to get total system power for an algorithm
    
    Args:
        algorithm: Algorithm name
        num_nodes: Number of edge servers
        load_factor: Server load factor (0.0 to 1.0)
        comparison_mode: 'realistic' or 'fair_comparison' (None = use current mode)
    
    Returns:
        Total system power consumption in Watts
    """
    model = EdgeServerPowerModel()
    
    if comparison_mode:
        model.set_comparison_mode(comparison_mode)
    
    power_breakdown = model.calculate_edge_server_power(algorithm, num_nodes, load_factor)
    return power_breakdown["total_system_power_w"]

# For backward compatibility with existing code
def cpu_power(util: float, algorithm: str = "default", num_nodes: int = 10000) -> float:
    """
    Compatibility function that replaces old CPU-based power calculation
    with 6G edge server model
    
    Args:
        util: CPU utilization (0.0 to 1.0) - used as load_factor
        algorithm: Algorithm name
        num_nodes: Number of edge servers
    
    Returns:
        Power consumption in Watts
    """
    return get_6g_edge_power(algorithm, num_nodes, util)

if __name__ == "__main__":
    # Example usage and testing
    model = EdgeServerPowerModel()
    
    # Test single algorithm
    power_data = model.calculate_edge_server_power("FedSemGNN", 10000)
    research_metrics = model.calculate_6g_research_metrics(power_data)
    
    print("6G Edge Server Power Model Test")
    print("=" * 40)
    print(f"Algorithm: FedSemGNN")
    print(f"Nodes: 10,000")
    print(f"Total System Power: {power_data['total_system_power_w']:.1f} W")
    print(f"Power per Edge Server: {power_data['power_per_edge_server_w']:.1f} W")
    print(f"Annual Cost: ${research_metrics['annual_operational_cost_usd']:.0f}")
    print(f"Scalability Class: {research_metrics['deployment_scalability_class']}")
    
    # Test comparison
    algorithms = ["FedSemGNN", "Flatfedppo", "Hierfedppo"]
    comparison = model.compare_algorithms(algorithms, 10000)
    
    print("\nComparison Results:")
    for algo, data in comparison.items():
        print(f"{algo}: {data['total_system_power_w']:.0f}W, ${data['annual_operational_cost_usd']:.0f}/year")