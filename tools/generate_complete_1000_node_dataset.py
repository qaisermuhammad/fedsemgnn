#!/usr/bin/env python3
"""
Complete 1000-Node Dataset Generator for FedSemGNN
Generates a comprehensive edge-sim-py compatible dataset with all required components
matching the exact structure of sample_dataset3.json but scaled for 1000+ nodes.
"""

import json
import random
import uuid
from typing import Dict, List, Any
import hashlib

def generate_digest():
    """Generate a realistic SHA256 digest"""
    return f"sha256:{hashlib.sha256(str(random.random()).encode()).hexdigest()}"

def generate_coordinates(max_x=100, max_y=100):
    """Generate random coordinates within bounds"""
    return [random.randint(0, max_x), random.randint(0, max_y)]

def generate_network_switches(count=500):
    """Generate NetworkSwitch components with proper relationships"""
    switches = []
    for i in range(1, count + 1):
        switch = {
            "attributes": {
                "id": i,
                "coordinates": generate_coordinates(),
                "active": True,
                "power_model_parameters": {
                    "chassis_power": random.randint(50, 80),
                    "ports_power_consumption": {
                        "125": round(random.uniform(0.8, 1.2), 1),
                        "12.5": round(random.uniform(0.2, 0.4), 1)
                    }
                }
            },
            "relationships": {
                "power_model": "ConteratoNetworkPowerModel",
                "edge_servers": [],  # Will be populated based on assignments
                "links": [],
                "base_station": {
                    "class": "BaseStation",
                    "id": ((i - 1) // 5) + 1  # 5 switches per base station
                }
            }
        }
        switches.append(switch)
    return switches

def generate_base_stations(count=200):
    """Generate BaseStation components"""
    stations = []
    for i in range(1, count + 1):
        station = {
            "attributes": {
                "id": i,
                "coordinates": generate_coordinates(),
                "active": True,
                "power_model_parameters": {
                    "max_power_consumption": random.randint(180, 250),
                    "static_power_percentage": round(random.uniform(0.3, 0.7), 4)
                }
            },
            "relationships": {
                "power_model": "LinearBaseStationPowerModel",
                "users": [],  # Will be populated
                "applications": []
            }
        }
        stations.append(station)
    return stations

def generate_edge_servers(count=1000):
    """Generate EdgeServer components with realistic hardware specs"""
    servers = []
    server_models = ["E5430", "E5507", "E5645", "E5520", "X5670"]
    
    for i in range(1, count + 1):
        model = random.choice(server_models)
        
        # Realistic specs based on model
        if model == "E5430":
            cpu, memory = 8, 16384
            max_power = 265
        elif model == "E5507":
            cpu, memory = 8, 8192
            max_power = 218
        elif model == "E5645":
            cpu, memory = 12, 32768
            max_power = 280
        elif model == "E5520":
            cpu, memory = 4, 8192
            max_power = 195
        else:  # X5670
            cpu, memory = 12, 24576
            max_power = 295
            
        server = {
            "attributes": {
                "id": i,
                "available": True,
                "model_name": model,
                "cpu": cpu,
                "memory": memory,
                "disk": random.choice([65536, 131072, 262144]),
                "cpu_demand": 0,
                "memory_demand": 0,
                "disk_demand": 0,
                "coordinates": generate_coordinates(),
                "max_concurrent_layer_downloads": random.randint(2, 5),
                "active": True,
                "power_model_parameters": {
                    "max_power_consumption": max_power,
                    "static_power_percentage": round(random.uniform(0.3, 0.7), 4)
                }
            },
            "relationships": {
                "power_model": "LinearServerPowerModel",
                "base_station": {
                    "class": "BaseStation",
                    "id": ((i - 1) // 5) + 1  # 5 servers per base station
                },
                "network_switch": {
                    "class": "NetworkSwitch", 
                    "id": ((i - 1) // 2) + 1  # 2 servers per switch
                },
                "services": [],
                "container_layers": [],
                "container_images": [],
                "container_registries": []
            }
        }
        servers.append(server)
    return servers

def generate_network_links(count=1000):
    """Generate NetworkLink components"""
    links = []
    for i in range(1, count + 1):
        link = {
            "attributes": {
                "id": i,
                "bandwidth": random.choice([10, 100, 1000]),  # Mbps
                "latency": round(random.uniform(1.0, 10.0), 2),
                "active": True
            },
            "relationships": {
                "applications": []
            }
        }
        links.append(link)
    return links

def generate_users(count=2000):
    """Generate User components"""
    users = []
    for i in range(1, count + 1):
        user = {
            "attributes": {
                "id": i,
                "coordinates": generate_coordinates(),
                "mobility_model": random.choice(["static", "random_walk", "mobility_trace"]),
                "active": True
            },
            "relationships": {
                "base_station": {
                    "class": "BaseStation",
                    "id": random.randint(1, 200)
                },
                "applications": []
            }
        }
        users.append(user)
    return users

def generate_services(count=500):
    """Generate Service components"""
    services = []
    for i in range(1, count + 1):
        service = {
            "attributes": {
                "id": i,
                "label": f"service_{i}",
                "cpu_demand": random.randint(1, 8),
                "memory_demand": random.randint(512, 8192),
                "disk_demand": random.randint(1024, 16384),
                "state_management_policy": "Stateless",
                "being_provisioned": False
            },
            "relationships": {
                "server": {
                    "class": "EdgeServer",
                    "id": random.randint(1, 1000)
                },
                "image": {
                    "class": "ContainerImage", 
                    "id": random.randint(1, 300)
                },
                "users": []
            }
        }
        services.append(service)
    return services

def generate_container_layers(count=3000):
    """Generate ContainerLayer components with realistic Docker layer data"""
    layers = []
    instructions = [
        "ADD file:5d673d25da3a14ce1f6cf",
        "/bin/sh -c set -eux; \tversion=",
        "ADD file:966d3669b40f5fbaecee1",
        "/bin/sh -c set -x     && addgr",
        "ADD file:b83df51ab7caf8a4dc35f", 
        "ADD file:e8d512b08fe2ddc6f2c85",
        "/bin/sh -c set -eux; \tapt-get ",
        "/bin/sh -c set -ex; \tif ! comm",
        "/bin/sh -c apt-get update && a",
        "/bin/sh -c set -ex; \tapt-get u"
    ]
    
    for i in range(1, count + 1):
        layer = {
            "attributes": {
                "id": i,
                "digest": generate_digest(),
                "size": random.randint(1, 200),  # MB
                "instruction": random.choice(instructions)
            },
            "relationships": {
                "server": {
                    "class": "EdgeServer",
                    "id": random.randint(1, 1000)
                }
            }
        }
        layers.append(layer)
    return layers

def generate_container_images(count=300):
    """Generate ContainerImage components"""
    images = []
    image_names = ["nginx", "alpine", "ubuntu", "python", "nodejs", "redis", "postgres", "mysql", "httpd", "registry"]
    
    for i in range(1, count + 1):
        # Generate realistic layer associations
        num_layers = random.randint(1, 8)
        layer_digests = [generate_digest() for _ in range(num_layers)]
        
        image = {
            "attributes": {
                "id": i,
                "name": random.choice(image_names),
                "tag": random.choice(["", "latest", "3.8", "alpine", "slim"]),
                "digest": generate_digest(),
                "layers_digests": layer_digests,
                "architecture": random.choice(["", "amd64", "arm64"])
            },
            "relationships": {
                "server": {
                    "class": "EdgeServer",
                    "id": random.randint(1, 1000)
                }
            }
        }
        images.append(image)
    return images

def generate_container_registries(count=20):
    """Generate ContainerRegistry components"""
    registries = []
    for i in range(1, count + 1):
        registry = {
            "attributes": {
                "id": i,
                "cpu_demand": random.randint(1, 4),
                "memory_demand": random.randint(512, 4096)
            },
            "relationships": {
                "server": {
                    "class": "EdgeServer",
                    "id": random.randint(1, 1000)
                }
            }
        }
        registries.append(registry)
    return registries

def generate_applications(count=150):
    """Generate Application components"""
    applications = []
    for i in range(1, count + 1):
        app = {
            "attributes": {
                "id": i,
                "label": f"app_{i}"
            },
            "relationships": {
                "services": [
                    {
                        "class": "Service",
                        "id": random.randint(1, 500)
                    }
                ],
                "users": [
                    {
                        "class": "User", 
                        "id": random.randint(1, 2000)
                    }
                ]
            }
        }
        applications.append(app)
    return applications

def generate_circular_access_patterns(count=300):
    """Generate CircularDurationAndIntervalAccessPattern components"""
    patterns = []
    for i in range(1, count + 1):
        pattern = {
            "attributes": {
                "id": i,
                "duration": round(random.uniform(60, 3600), 2),  # 1 minute to 1 hour
                "interval": round(random.uniform(10, 600), 2),   # 10 seconds to 10 minutes
                "active": True
            },
            "relationships": {
                "application": {
                    "class": "Application",
                    "id": random.randint(1, 150)
                }
            }
        }
        patterns.append(pattern)
    return patterns

def generate_random_access_patterns(count=100):
    """Generate RandomDurationAndIntervalAccessPattern components"""
    patterns = []
    for i in range(1, count + 1):
        pattern = {
            "attributes": {
                "id": i,
                "min_duration": round(random.uniform(30, 120), 2),
                "max_duration": round(random.uniform(300, 1800), 2),
                "min_interval": round(random.uniform(5, 30), 2),
                "max_interval": round(random.uniform(60, 300), 2),
                "active": True
            },
            "relationships": {
                "application": {
                    "class": "Application",
                    "id": random.randint(1, 150)
                }
            }
        }
        patterns.append(pattern)
    return patterns

def assign_relationships(dataset):
    """Assign proper relationships between components"""
    
    # Assign EdgeServers to NetworkSwitches
    for i, switch in enumerate(dataset["NetworkSwitch"]):
        # Each switch gets 2 edge servers
        start_server = i * 2 + 1
        end_server = min(start_server + 2, len(dataset["EdgeServer"]) + 1)
        switch["relationships"]["edge_servers"] = [
            {"class": "EdgeServer", "id": j} 
            for j in range(start_server, end_server)
        ]
    
    # Assign Applications to Users (some users have applications)
    for i, user in enumerate(dataset["User"]):
        if random.random() < 0.3:  # 30% of users have applications
            app_id = random.randint(1, len(dataset["Application"]))
            user["relationships"]["applications"] = [
                {"class": "Application", "id": app_id}
            ]
    
    # Assign Applications to BaseStations
    for station in dataset["BaseStation"]:
        if random.random() < 0.4:  # 40% of base stations have applications
            num_apps = random.randint(1, 3)
            app_ids = random.sample(range(1, len(dataset["Application"]) + 1), 
                                  min(num_apps, len(dataset["Application"])))
            station["relationships"]["applications"] = [
                {"class": "Application", "id": app_id} for app_id in app_ids
            ]
    
    print("✅ Relationships assigned successfully")

def generate_complete_1000_node_dataset():
    """Generate complete dataset with all edge-sim-py components"""
    print("🚀 Starting comprehensive 1000-node dataset generation...")
    
    dataset = {}
    
    # Generate all component types with proper scaling
    print("📊 Generating NetworkSwitch components...")
    dataset["NetworkSwitch"] = generate_network_switches(500)
    
    print("📡 Generating BaseStation components...")
    dataset["BaseStation"] = generate_base_stations(200)
    
    print("🖥️  Generating EdgeServer components...")
    dataset["EdgeServer"] = generate_edge_servers(1000)
    
    print("🔗 Generating NetworkLink components...")
    dataset["NetworkLink"] = generate_network_links(1000)
    
    print("👥 Generating User components...")
    dataset["User"] = generate_users(2000)
    
    print("⚙️  Generating Service components...")
    dataset["Service"] = generate_services(500)
    
    print("🐳 Generating ContainerLayer components...")
    dataset["ContainerLayer"] = generate_container_layers(3000)
    
    print("📦 Generating ContainerImage components...")
    dataset["ContainerImage"] = generate_container_images(300)
    
    print("🗃️  Generating ContainerRegistry components...")
    dataset["ContainerRegistry"] = generate_container_registries(20)
    
    print("📱 Generating Application components...")
    dataset["Application"] = generate_applications(150)
    
    print("🔄 Generating CircularDurationAndIntervalAccessPattern components...")
    dataset["CircularDurationAndIntervalAccessPattern"] = generate_circular_access_patterns(300)
    
    print("🎲 Generating RandomDurationAndIntervalAccessPattern components...")
    dataset["RandomDurationAndIntervalAccessPattern"] = generate_random_access_patterns(100)
    
    print("🔄 Assigning component relationships...")
    assign_relationships(dataset)
    
    # Save dataset
    output_file = "workloads/extreme_scale_dataset_1000_complete.json"
    print(f"💾 Saving complete dataset to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    # Generate summary
    total_components = sum(len(components) for components in dataset.values())
    print(f"\n🎉 Complete 1000+ node dataset generated successfully!")
    print(f"📊 Dataset Summary:")
    print(f"   • Total Components: {total_components:,}")
    for component_type, components in dataset.items():
        print(f"   • {component_type}: {len(components):,}")
    
    print(f"\n💼 Dataset saved to: {output_file}")
    print(f"📏 File size: ~{total_components * 150 // 1024:.1f} KB estimated")
    
    return dataset

if __name__ == "__main__":
    dataset = generate_complete_1000_node_dataset()
    print("\n✅ Generation complete - dataset ready for FedSemGNN simulation!")