#!/usr/bin/env python3
"""
Workload Standardization for Fair Comparison
Ensures all algorithms use identical workload patterns
"""

import json
import numpy as np
import random
from datetime import datetime

class StandardWorkloadGenerator:
    """Generates standardized workloads for fair comparison"""
    
    def __init__(self, seed=42):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
    def generate_service_workload(self, num_services=50, num_steps=1000):
        """Generate standardized service arrival and departure patterns"""
        
        workload = {
            "metadata": {
                "generator": "StandardWorkloadGenerator",
                "seed": self.seed,
                "num_services": num_services,
                "num_steps": num_steps,
                "generation_time": datetime.now().isoformat()
            },
            "services": [],
            "arrivals": [],
            "departures": []
        }
        
        # Service characteristics (fixed for all algorithms)
        service_types = [
            {"name": "web_service", "cpu_req": 2.0, "memory_req": 512, "bandwidth_req": 10},
            {"name": "database", "cpu_req": 4.0, "memory_req": 2048, "bandwidth_req": 5},
            {"name": "ml_inference", "cpu_req": 8.0, "memory_req": 1024, "bandwidth_req": 20},
            {"name": "video_stream", "cpu_req": 3.0, "memory_req": 256, "bandwidth_req": 50},
            {"name": "iot_aggregator", "cpu_req": 1.0, "memory_req": 128, "bandwidth_req": 2}
        ]
        
        # Generate services
        for i in range(num_services):
            service_type = random.choice(service_types)
            service = {
                "id": f"service_{i:03d}",
                "type": service_type["name"],
                "cpu_requirement": service_type["cpu_req"] * (0.8 + 0.4 * random.random()),
                "memory_requirement": int(service_type["memory_req"] * (0.8 + 0.4 * random.random())),
                "bandwidth_requirement": service_type["bandwidth_req"] * (0.8 + 0.4 * random.random()),
                "arrival_step": random.randint(1, min(50, num_steps // 10)),
                "duration": random.randint(100, min(500, num_steps // 2)),
                "priority": random.uniform(0.1, 1.0),
                "geo_preference": random.choice(["edge", "cloud", "any"])
            }
            workload["services"].append(service)
        
        # Generate arrival/departure events
        for service in workload["services"]:
            arrival = {
                "step": service["arrival_step"],
                "event": "arrival",
                "service_id": service["id"],
                "service_data": service
            }
            workload["arrivals"].append(arrival)
            
            departure_step = service["arrival_step"] + service["duration"]
            if departure_step <= num_steps:
                departure = {
                    "step": departure_step,
                    "event": "departure", 
                    "service_id": service["id"]
                }
                workload["departures"].append(departure)
        
        # Sort events by step
        workload["arrivals"].sort(key=lambda x: x["step"])
        workload["departures"].sort(key=lambda x: x["step"])
        
        return workload
    
    def generate_network_conditions(self, num_steps=1000):
        """Generate standardized network condition variations"""
        
        conditions = {
            "metadata": {
                "generator": "StandardWorkloadGenerator",
                "seed": self.seed,
                "num_steps": num_steps,
                "generation_time": datetime.now().isoformat()
            },
            "timeline": []
        }
        
        # Base network parameters
        base_latency = 5.0  # ms
        base_bandwidth = 1000.0  # Mbps
        base_packet_loss = 0.01  # 1%
        
        for step in range(1, num_steps + 1):
            # Add some periodic variations and random noise
            time_factor = step / num_steps
            
            # Latency variations (daily cycles, random spikes)
            latency_variation = 1.0 + 0.3 * np.sin(2 * np.pi * time_factor * 3)  # 3 cycles
            latency_noise = 1.0 + 0.2 * (random.random() - 0.5)
            current_latency = base_latency * latency_variation * latency_noise
            
            # Bandwidth variations (congestion patterns)
            bandwidth_variation = 1.0 - 0.2 * np.sin(2 * np.pi * time_factor * 2)  # 2 cycles
            bandwidth_noise = 1.0 + 0.1 * (random.random() - 0.5)
            current_bandwidth = base_bandwidth * bandwidth_variation * bandwidth_noise
            
            # Packet loss (occasional spikes)
            if random.random() < 0.05:  # 5% chance of elevated packet loss
                current_packet_loss = base_packet_loss * (2 + 3 * random.random())
            else:
                current_packet_loss = base_packet_loss * (0.5 + random.random())
            
            conditions["timeline"].append({
                "step": step,
                "latency_ms": max(0.1, current_latency),
                "bandwidth_mbps": max(10, current_bandwidth),
                "packet_loss_rate": min(0.1, max(0.001, current_packet_loss))
            })
        
        return conditions
    
    def generate_server_failures(self, num_servers=16, num_steps=1000, failure_rate=0.001):
        """Generate standardized server failure patterns"""
        
        failures = {
            "metadata": {
                "generator": "StandardWorkloadGenerator",
                "seed": self.seed,
                "num_servers": num_servers,
                "num_steps": num_steps,
                "failure_rate": failure_rate,
                "generation_time": datetime.now().isoformat()
            },
            "events": []
        }
        
        for step in range(1, num_steps + 1):
            for server_id in range(num_servers):
                if random.random() < failure_rate:
                    # Server failure
                    failure_duration = random.randint(5, 30)  # 5-30 steps
                    failures["events"].append({
                        "step": step,
                        "server_id": server_id,
                        "event": "failure",
                        "duration": failure_duration,
                        "recovery_step": step + failure_duration
                    })
        
        # Sort by step
        failures["events"].sort(key=lambda x: x["step"])
        
        return failures
    
    def save_workload_suite(self, output_dir="workloads", num_steps=1000):
        """Generate and save complete standardized workload suite"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🔧 Generating standardized workloads (seed={self.seed})")
        
        # Service workload
        service_workload = self.generate_service_workload(num_steps=num_steps)
        service_path = os.path.join(output_dir, "standard_service_workload.json")
        with open(service_path, 'w') as f:
            json.dump(service_workload, f, indent=2)
        print(f"   📋 Service workload: {service_path}")
        
        # Network conditions
        network_conditions = self.generate_network_conditions(num_steps=num_steps)
        network_path = os.path.join(output_dir, "standard_network_conditions.json")
        with open(network_path, 'w') as f:
            json.dump(network_conditions, f, indent=2)
        print(f"   🌐 Network conditions: {network_path}")
        
        # Server failures
        server_failures = self.generate_server_failures(num_steps=num_steps)
        failures_path = os.path.join(output_dir, "standard_server_failures.json")
        with open(failures_path, 'w') as f:
            json.dump(server_failures, f, indent=2)
        print(f"   ⚠️  Server failures: {failures_path}")
        
        # Summary
        summary = {
            "workload_suite": "Standard Fair Comparison Workloads",
            "generator_seed": self.seed,
            "num_steps": num_steps,
            "files": {
                "service_workload": service_path,
                "network_conditions": network_path, 
                "server_failures": failures_path
            },
            "statistics": {
                "num_services": len(service_workload["services"]),
                "num_arrivals": len(service_workload["arrivals"]),
                "num_departures": len(service_workload["departures"]),
                "num_failure_events": len(server_failures["events"])
            },
            "generation_time": datetime.now().isoformat()
        }
        
        summary_path = os.path.join(output_dir, "workload_suite_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"   📊 Summary: {summary_path}")
        
        return output_dir

if __name__ == "__main__":
    generator = StandardWorkloadGenerator(seed=42)
    workload_dir = generator.save_workload_suite(num_steps=1000)
    print(f"\\n✅ Standardized workloads generated in: {workload_dir}")
