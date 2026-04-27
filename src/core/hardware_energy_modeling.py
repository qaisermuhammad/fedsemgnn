from typing import Dict, Any

def get_available_hardware_profiles():
    """Get all available hardware profiles for simulation"""
    return {
        "intel_xeon_silver": {"name": "Intel Xeon Silver 4210R", "cores": 10, "tdp": 100},
        "amd_epyc_7002": {"name": "AMD EPYC 7262", "cores": 8, "tdp": 155},
        "arm_cortex_a78": {"name": "ARM Cortex-A78", "cores": 8, "tdp": 15},
        "nvidia_jetson_xavier": {"name": "NVIDIA Jetson Xavier NX", "cores": 6, "tdp": 20},
        "raspberry_pi_4": {"name": "Raspberry Pi 4B", "cores": 4, "tdp": 8},
        "intel_nuc_i7": {"name": "Intel NUC i7", "cores": 4, "tdp": 45},
        "aws_graviton2": {"name": "AWS Graviton2", "cores": 2, "tdp": 35}
    }

class HardwareEnergySimulator:
    """Simulates hardware energy modeling"""
    
    def __init__(self, hardware_type: str = "intel_xeon_silver"):
        self.hardware_type = hardware_type
        self.profiles = get_available_hardware_profiles()
        
    def simulate_hardware_counters(self, hardware_type: str, cpu_utilization: float, 
                                 memory_utilization: float, workload_intensity: float) -> Dict[str, Any]:
        """Simulate hardware counters for the given workload"""
        
        # Get hardware profile
        profile = self.profiles.get(hardware_type, self.profiles["intel_xeon_silver"])
        
        # Calculate power consumption based on utilization
        base_power = profile["tdp"] * 0.3  # Base power
        dynamic_power = profile["tdp"] * 0.7 * cpu_utilization
        total_power = base_power + dynamic_power
        
        # Simulate other metrics
        cpu_cycles = int(cpu_utilization * 2.4e9)  # 2.4 GHz base
        cache_misses = int(cpu_cycles * 0.1 * workload_intensity)
        
        return {
            "cpu_cycles": cpu_cycles,
            "cache_misses": cache_misses,
            "power_consumption_w": total_power,
            "energy_consumption_j": total_power * 1.0,  # 1 second
            "thermal_state": 45.0 + cpu_utilization * 20.0,
            "thermal_throttling": False,
            "dvfs_state": "2.4GHz@1.0V"
        } 
