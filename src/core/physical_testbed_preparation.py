# physical_testbed_preparation.py
"""
Physical Testbed Preparation (Simulation-Based)
Prepares FedSemGNN for deployment on physical 6G edge testbeds without requiring hardware purchase.
Creates virtual testbed environments that model real deployment scenarios.
"""

import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from datetime import datetime, timedelta

# =============================================================================
# TESTBED CONFIGURATION MODELS
# =============================================================================

class TestbedType(Enum):
    """Different types of edge testbeds for simulation"""
    UNIVERSITY_CAMPUS = "university_campus_6g"
    SMART_CITY = "smart_city_edge"
    INDUSTRIAL_IOT = "industrial_iot_network"
    AUTONOMOUS_VEHICLE = "autonomous_vehicle_edge"
    HEALTHCARE_EDGE = "healthcare_edge_network"
    RETAIL_EDGE = "retail_edge_computing"

class NetworkTechnology(Enum):
    """Network technologies available in testbeds"""
    FIBER_OPTIC = "fiber_optic"
    WIFI_6E = "wifi_6e"
    WIFI_7 = "wifi_7"
    LTE_5G = "lte_5g"
    SATELLITE = "satellite"
    ETHERNET_GIGABIT = "ethernet_1gb"
    ETHERNET_10GB = "ethernet_10gb"

@dataclass
class NetworkLink:
    """Network link characteristics"""
    source_node: int
    destination_node: int
    technology: NetworkTechnology
    bandwidth_mbps: float
    latency_ms: float
    packet_loss_rate: float
    jitter_ms: float
    cost_per_gb: float
    reliability: float  # 0.0 to 1.0

@dataclass
class DeploymentNode:
    """Physical deployment node specification"""
    node_id: int
    location_name: str
    latitude: float
    longitude: float
    hardware_type: str
    available_resources: Dict[str, float]  # CPU cores, memory GB, storage GB
    network_interfaces: List[str]
    power_source: str  # "grid", "battery", "solar", "hybrid"
    environment: str  # "indoor", "outdoor", "vehicle", "marine"
    security_level: int  # 1-5 scale
    maintenance_access: str  # "easy", "moderate", "difficult", "remote"

@dataclass
class TestbedConfiguration:
    """Complete testbed configuration"""
    testbed_id: str
    testbed_type: TestbedType
    description: str
    deployment_nodes: List[DeploymentNode]
    network_topology: List[NetworkLink]
    service_requirements: Dict[str, Any]
    sla_requirements: Dict[str, float]
    deployment_constraints: Dict[str, Any]
    monitoring_setup: Dict[str, Any]
    failure_scenarios: List[Dict[str, Any]]

# =============================================================================
# TESTBED TEMPLATES
# =============================================================================

class TestbedTemplateGenerator:
    """Generates realistic testbed configurations for different scenarios"""
    
    @staticmethod
    def generate_university_campus_testbed() -> TestbedConfiguration:
        """Generate a university campus 6G edge testbed"""
        
        # Define campus buildings as deployment nodes
        nodes = [
            DeploymentNode(0, "Computer Science Building", 40.7589, -73.9851,
                         "intel_xeon_silver", {"cpu": 20, "memory": 64, "storage": 2000},
                         ["wifi_6e", "ethernet_10gb"], "grid", "indoor", 5, "easy"),
            
            DeploymentNode(1, "Engineering Lab", 40.7595, -73.9845,
                         "amd_epyc_7002", {"cpu": 16, "memory": 128, "storage": 4000},
                         ["wifi_6e", "ethernet_10gb", "lte_5g"], "grid", "indoor", 4, "easy"),
            
            DeploymentNode(2, "Library Main", 40.7580, -73.9860,
                         "intel_nuc_i7", {"cpu": 8, "memory": 32, "storage": 1000},
                         ["wifi_6e", "ethernet_1gb"], "grid", "indoor", 3, "moderate"),
            
            DeploymentNode(3, "Student Center", 40.7575, -73.9840,
                         "nvidia_jetson_xavier", {"cpu": 6, "memory": 8, "storage": 512},
                         ["wifi_6e", "lte_5g"], "grid", "indoor", 3, "moderate"),
            
            DeploymentNode(4, "Sports Complex", 40.7565, -73.9830,
                         "raspberry_pi_4", {"cpu": 4, "memory": 4, "storage": 128},
                         ["wifi_6e", "lte_5g"], "battery", "outdoor", 2, "difficult"),
            
            DeploymentNode(5, "Research Greenhouse", 40.7600, -73.9870,
                         "arm_cortex_a78", {"cpu": 8, "memory": 8, "storage": 256},
                         ["wifi_6e", "lte_5g"], "solar", "outdoor", 2, "difficult")
        ]
        
        # Define network topology
        network_links = [
            # High-speed backbone connections
            NetworkLink(0, 1, NetworkTechnology.ETHERNET_10GB, 10000, 0.5, 0.0001, 0.1, 0.01, 0.999),
            NetworkLink(1, 2, NetworkTechnology.ETHERNET_GIGABIT, 1000, 1.0, 0.0005, 0.2, 0.05, 0.995),
            NetworkLink(2, 3, NetworkTechnology.WIFI_6E, 2400, 2.0, 0.001, 0.5, 0.1, 0.99),
            
            # Edge connections
            NetworkLink(3, 4, NetworkTechnology.LTE_5G, 300, 15.0, 0.01, 2.0, 0.5, 0.95),
            NetworkLink(4, 5, NetworkTechnology.WIFI_6E, 1200, 5.0, 0.005, 1.0, 0.2, 0.98),
            
            # Redundant paths
            NetworkLink(0, 2, NetworkTechnology.FIBER_OPTIC, 5000, 0.3, 0.0001, 0.05, 0.02, 0.9999),
            NetworkLink(1, 3, NetworkTechnology.ETHERNET_GIGABIT, 1000, 1.2, 0.0008, 0.3, 0.06, 0.992)
        ]
        
        return TestbedConfiguration(
            testbed_id="campus_6g_v1",
            testbed_type=TestbedType.UNIVERSITY_CAMPUS,
            description="University campus 6G edge computing testbed with diverse hardware and network technologies",
            deployment_nodes=nodes,
            network_topology=network_links,
            service_requirements={
                "federated_learning": {"min_nodes": 4, "min_memory_gb": 8, "min_cpu_cores": 4},
                "real_time_services": {"max_latency_ms": 10, "min_reliability": 0.99},
                "data_intensive": {"min_bandwidth_mbps": 500, "min_storage_gb": 500}
            },
            sla_requirements={
                "availability": 0.999,
                "max_response_time_ms": 50,
                "min_throughput_ops_sec": 1000,
                "max_energy_consumption_w": 500
            },
            deployment_constraints={
                "budget_usd": 50000,
                "deployment_time_days": 30,
                "maintenance_frequency_days": 7,
                "security_compliance": ["FERPA", "GDPR"]
            },
            monitoring_setup={
                "metrics_collection_interval_s": 1,
                "log_retention_days": 90,
                "alert_thresholds": {"cpu_util": 0.8, "memory_util": 0.85, "latency_ms": 100}
            },
            failure_scenarios=[
                {"type": "node_failure", "probability": 0.001, "recovery_time_min": 60},
                {"type": "network_partition", "probability": 0.0005, "recovery_time_min": 120},
                {"type": "power_outage", "probability": 0.0001, "recovery_time_min": 300}
            ]
        )
    
    @staticmethod
    def generate_smart_city_testbed() -> TestbedConfiguration:
        """Generate a smart city edge testbed"""
        
        nodes = [
            # Traffic management
            DeploymentNode(0, "Traffic Control Center", 40.7128, -74.0060,
                         "intel_xeon_silver", {"cpu": 24, "memory": 128, "storage": 5000},
                         ["fiber_optic", "ethernet_10gb", "lte_5g"], "grid", "indoor", 5, "easy"),
            
            # Smart intersections
            DeploymentNode(1, "5th Ave & 42nd St", 40.7505, -73.9934,
                         "nvidia_jetson_xavier", {"cpu": 6, "memory": 8, "storage": 512},
                         ["lte_5g", "wifi_6e"], "grid", "outdoor", 3, "moderate"),
            
            DeploymentNode(2, "Broadway & Times Sq", 40.7580, -73.9855,
                         "nvidia_jetson_xavier", {"cpu": 6, "memory": 8, "storage": 512},
                         ["lte_5g", "wifi_6e"], "grid", "outdoor", 3, "moderate"),
            
            # Environmental monitoring
            DeploymentNode(3, "Central Park Monitoring", 40.7812, -73.9665,
                         "raspberry_pi_4", {"cpu": 4, "memory": 4, "storage": 128},
                         ["lte_5g", "wifi_6e"], "solar", "outdoor", 2, "difficult"),
            
            # Emergency services
            DeploymentNode(4, "Emergency Response Hub", 40.7282, -74.0776,
                         "amd_epyc_7002", {"cpu": 16, "memory": 64, "storage": 2000},
                         ["fiber_optic", "lte_5g", "satellite"], "grid", "indoor", 5, "easy"),
            
            # Public transportation
            DeploymentNode(5, "Grand Central Station", 40.7527, -73.9772,
                         "intel_nuc_i7", {"cpu": 8, "memory": 16, "storage": 1000},
                         ["wifi_6e", "ethernet_1gb", "lte_5g"], "grid", "indoor", 4, "moderate")
        ]
        
        # Smart city network topology
        network_links = [
            # Fiber backbone
            NetworkLink(0, 4, NetworkTechnology.FIBER_OPTIC, 20000, 0.2, 0.00001, 0.02, 0.005, 0.9999),
            NetworkLink(0, 5, NetworkTechnology.FIBER_OPTIC, 10000, 0.5, 0.00005, 0.05, 0.01, 0.999),
            
            # 5G connections to intersections
            NetworkLink(0, 1, NetworkTechnology.LTE_5G, 500, 8.0, 0.005, 1.5, 0.3, 0.97),
            NetworkLink(0, 2, NetworkTechnology.LTE_5G, 500, 10.0, 0.008, 2.0, 0.3, 0.96),
            
            # Environmental monitoring
            NetworkLink(3, 1, NetworkTechnology.LTE_5G, 100, 20.0, 0.02, 5.0, 0.8, 0.93),
            
            # Emergency backup connections
            NetworkLink(4, 1, NetworkTechnology.SATELLITE, 50, 600.0, 0.1, 50.0, 5.0, 0.85),
            NetworkLink(4, 2, NetworkTechnology.SATELLITE, 50, 600.0, 0.1, 50.0, 5.0, 0.85)
        ]
        
        return TestbedConfiguration(
            testbed_id="smart_city_v1",
            testbed_type=TestbedType.SMART_CITY,
            description="Smart city edge computing testbed with traffic management, environmental monitoring, and emergency services",
            deployment_nodes=nodes,
            network_topology=network_links,
            service_requirements={
                "real_time_traffic": {"max_latency_ms": 5, "min_reliability": 0.999},
                "environmental_analytics": {"min_storage_gb": 1000, "data_retention_days": 365},
                "emergency_response": {"max_response_time_ms": 1, "redundancy_level": 3}
            },
            sla_requirements={
                "availability": 0.9999,
                "max_response_time_ms": 10,
                "min_throughput_ops_sec": 10000,
                "max_energy_consumption_w": 2000
            },
            deployment_constraints={
                "budget_usd": 500000,
                "deployment_time_days": 180,
                "regulatory_approval": ["DOT", "FCC", "EPA"],
                "public_safety_compliance": True
            },
            monitoring_setup={
                "metrics_collection_interval_s": 0.1,
                "log_retention_days": 365,
                "real_time_dashboards": True,
                "alert_thresholds": {"response_time_ms": 10, "packet_loss": 0.01}
            },
            failure_scenarios=[
                {"type": "traffic_signal_failure", "probability": 0.01, "impact": "high"},
                {"type": "communication_blackout", "probability": 0.001, "impact": "critical"},
                {"type": "cyber_attack", "probability": 0.0001, "impact": "critical"}
            ]
        )

class TestbedOrchestrator:
    """Orchestrates testbed deployment and management"""
    
    def __init__(self):
        self.active_testbeds: Dict[str, TestbedConfiguration] = {}
        self.deployment_history: List[Dict[str, Any]] = []
        
    def register_testbed(self, config: TestbedConfiguration):
        """Register a new testbed configuration"""
        self.active_testbeds[config.testbed_id] = config
        print(f"✓ Registered testbed: {config.testbed_id} ({config.testbed_type.value})")
        
    def validate_testbed_configuration(self, config: TestbedConfiguration) -> Dict[str, Any]:
        """Validate testbed configuration for deployment readiness"""
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check node connectivity
        node_ids = {node.node_id for node in config.deployment_nodes}
        connected_nodes = set()
        
        for link in config.network_topology:
            connected_nodes.add(link.source_node)
            connected_nodes.add(link.destination_node)
        
        disconnected_nodes = node_ids - connected_nodes
        if disconnected_nodes:
            validation_results["errors"].append(f"Disconnected nodes: {disconnected_nodes}")
            validation_results["valid"] = False
        
        # Check resource requirements
        total_cpu = sum(node.available_resources.get("cpu", 0) for node in config.deployment_nodes)
        total_memory = sum(node.available_resources.get("memory", 0) for node in config.deployment_nodes)
        
        min_cpu_req = config.service_requirements.get("federated_learning", {}).get("min_cpu_cores", 0)
        min_memory_req = config.service_requirements.get("federated_learning", {}).get("min_memory_gb", 0)
        
        if total_cpu < min_cpu_req:
            validation_results["errors"].append(f"Insufficient CPU: {total_cpu} < {min_cpu_req}")
            validation_results["valid"] = False
        
        if total_memory < min_memory_req:
            validation_results["errors"].append(f"Insufficient memory: {total_memory} < {min_memory_req}")
            validation_results["valid"] = False
        
        # Check network latency requirements
        max_latency_req = config.sla_requirements.get("max_response_time_ms", float('inf'))
        high_latency_links = [link for link in config.network_topology if link.latency_ms > max_latency_req]
        
        if high_latency_links:
            validation_results["warnings"].append(f"High latency links detected: {len(high_latency_links)}")
        
        # Security recommendations
        low_security_nodes = [node for node in config.deployment_nodes if node.security_level < 3]
        if low_security_nodes:
            validation_results["recommendations"].append(f"Consider upgrading security for {len(low_security_nodes)} nodes")
        
        return validation_results
    
    def generate_deployment_plan(self, testbed_id: str) -> Dict[str, Any]:
        """Generate a detailed deployment plan"""
        if testbed_id not in self.active_testbeds:
            raise ValueError(f"Testbed {testbed_id} not found")
        
        config = self.active_testbeds[testbed_id]
        
        # Phase-based deployment plan
        deployment_plan = {
            "testbed_id": testbed_id,
            "total_duration_days": config.deployment_constraints.get("deployment_time_days", 30),
            "estimated_cost_usd": config.deployment_constraints.get("budget_usd", 100000),
            "phases": []
        }
        
        # Phase 1: Infrastructure preparation
        phase1 = {
            "phase": 1,
            "name": "Infrastructure Preparation",
            "duration_days": 7,
            "tasks": [
                "Site surveys and permits",
                "Power infrastructure setup",
                "Network cabling installation",
                "Security system installation"
            ],
            "dependencies": [],
            "critical_path": True
        }
        
        # Phase 2: Hardware deployment
        phase2 = {
            "phase": 2,
            "name": "Hardware Deployment",
            "duration_days": 10,
            "tasks": [
                "Edge server installation",
                "Network equipment configuration",
                "Initial hardware testing",
                "Environmental monitoring setup"
            ],
            "dependencies": [1],
            "critical_path": True
        }
        
        # Phase 3: Software configuration
        phase3 = {
            "phase": 3,
            "name": "Software Configuration",
            "duration_days": 7,
            "tasks": [
                "Operating system installation",
                "Container orchestration setup",
                "FedSemGNN deployment",
                "Monitoring and logging configuration"
            ],
            "dependencies": [2],
            "critical_path": True
        }
        
        # Phase 4: Testing and validation
        phase4 = {
            "phase": 4,
            "name": "Testing and Validation",
            "duration_days": 5,
            "tasks": [
                "Functional testing",
                "Performance benchmarking",
                "Fault tolerance testing",
                "Security penetration testing"
            ],
            "dependencies": [3],
            "critical_path": False
        }
        
        # Phase 5: Production deployment
        phase5 = {
            "phase": 5,
            "name": "Production Deployment",
            "duration_days": 1,
            "tasks": [
                "Final configuration review",
                "Production cutover",
                "Monitoring activation",
                "Documentation handover"
            ],
            "dependencies": [4],
            "critical_path": True
        }
        
        deployment_plan["phases"] = [phase1, phase2, phase3, phase4, phase5]
        
        # Generate resource allocation
        deployment_plan["resource_allocation"] = {
            "personnel": {
                "network_engineers": 2,
                "system_administrators": 3,
                "security_specialists": 1,
                "project_manager": 1
            },
            "equipment": {
                "edge_servers": len(config.deployment_nodes),
                "network_switches": max(1, len(config.network_topology) // 4),
                "monitoring_probes": len(config.deployment_nodes),
                "security_appliances": max(1, len(config.deployment_nodes) // 3)
            }
        }
        
        return deployment_plan
    
    def generate_container_deployment_manifests(self, testbed_id: str) -> Dict[str, str]:
        """Generate Kubernetes/Docker deployment manifests"""
        if testbed_id not in self.active_testbeds:
            raise ValueError(f"Testbed {testbed_id} not found")
        
        config = self.active_testbeds[testbed_id]
        manifests = {}
        
        # Generate FedSemGNN deployment manifest
        fedsemgnn_manifest = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fedsemgnn-{testbed_id}
  labels:
    app: fedsemgnn
    testbed: {testbed_id}
spec:
  replicas: {len(config.deployment_nodes)}
  selector:
    matchLabels:
      app: fedsemgnn
  template:
    metadata:
      labels:
        app: fedsemgnn
    spec:
      containers:
      - name: fedsemgnn
        image: fedsemgnn:latest
        ports:
        - containerPort: 8080
        env:
        - name: TESTBED_ID
          value: "{testbed_id}"
        - name: NODE_COUNT
          value: "{len(config.deployment_nodes)}"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
      volumes:
      - name: config-volume
        configMap:
          name: fedsemgnn-config
---
apiVersion: v1
kind: Service
metadata:
  name: fedsemgnn-service-{testbed_id}
spec:
  selector:
    app: fedsemgnn
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
"""
        
        manifests["fedsemgnn-deployment.yaml"] = fedsemgnn_manifest
        
        # Generate monitoring stack
        monitoring_manifest = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config-{testbed_id}
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'fedsemgnn'
      static_configs:
      - targets: ['fedsemgnn-service-{testbed_id}:80']
    - job_name: 'node-exporter'
      static_configs:
      - targets: {[f"'node-{node.node_id}:9100'" for node in config.deployment_nodes]}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: monitoring-stack-{testbed_id}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: monitoring
  template:
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
"""
        
        manifests["monitoring-deployment.yaml"] = monitoring_manifest
        
        return manifests
    
    def save_testbed_configuration(self, testbed_id: str, output_dir: str = "testbed_configs"):
        """Save complete testbed configuration for deployment"""
        if testbed_id not in self.active_testbeds:
            raise ValueError(f"Testbed {testbed_id} not found")
        
        config = self.active_testbeds[testbed_id]
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save main configuration as JSON
        config_file = os.path.join(output_dir, f"{testbed_id}_config.json")
        with open(config_file, 'w') as f:
            json.dump(asdict(config), f, indent=2, default=str)
        
        # Save deployment plan
        deployment_plan = self.generate_deployment_plan(testbed_id)
        plan_file = os.path.join(output_dir, f"{testbed_id}_deployment_plan.json")
        with open(plan_file, 'w') as f:
            json.dump(deployment_plan, f, indent=2)
        
        # Save container manifests
        manifests = self.generate_container_deployment_manifests(testbed_id)
        manifests_dir = os.path.join(output_dir, f"{testbed_id}_manifests")
        os.makedirs(manifests_dir, exist_ok=True)
        
        for filename, content in manifests.items():
            manifest_file = os.path.join(manifests_dir, filename)
            with open(manifest_file, 'w') as f:
                f.write(content)
        
        # Generate inventory file for Ansible
        inventory_content = self._generate_ansible_inventory(config)
        inventory_file = os.path.join(output_dir, f"{testbed_id}_inventory.ini")
        with open(inventory_file, 'w') as f:
            f.write(inventory_content)
        
        print(f"✓ Testbed configuration saved to {output_dir}/")
        print(f"  • Configuration: {config_file}")
        print(f"  • Deployment plan: {plan_file}")
        print(f"  • Container manifests: {manifests_dir}/")
        print(f"  • Ansible inventory: {inventory_file}")
    
    def _generate_ansible_inventory(self, config: TestbedConfiguration) -> str:
        """Generate Ansible inventory for automated deployment"""
        inventory = f"# Ansible inventory for {config.testbed_id}\n\n"
        
        # Group nodes by hardware type
        hardware_groups = {}
        for node in config.deployment_nodes:
            hw_type = node.hardware_type.replace("_", "-")
            if hw_type not in hardware_groups:
                hardware_groups[hw_type] = []
            hardware_groups[hw_type].append(node)
        
        # Generate inventory groups
        for hw_type, nodes in hardware_groups.items():
            inventory += f"[{hw_type}]\n"
            for node in nodes:
                inventory += f"node-{node.node_id} ansible_host={node.latitude},{node.longitude} "
                inventory += f"location='{node.location_name}' "
                inventory += f"cpu_cores={node.available_resources.get('cpu', 4)} "
                inventory += f"memory_gb={node.available_resources.get('memory', 8)}\n"
            inventory += "\n"
        
        # Add group variables
        inventory += "[all:vars]\n"
        inventory += f"testbed_id={config.testbed_id}\n"
        inventory += f"testbed_type={config.testbed_type.value}\n"
        inventory += "ansible_user=admin\n"
        inventory += "ansible_ssh_private_key_file=~/.ssh/testbed_key\n"
        
        return inventory

# =============================================================================
# INTEGRATION FUNCTIONS
# =============================================================================

def initialize_physical_testbed_preparation():
    """Initialize physical testbed preparation system"""
    print("🏗️ Initializing Physical Testbed Preparation...")
    
    orchestrator = TestbedOrchestrator()
    
    # Generate sample testbed configurations
    campus_config = TestbedTemplateGenerator.generate_university_campus_testbed()
    city_config = TestbedTemplateGenerator.generate_smart_city_testbed()
    
    # Register testbeds
    orchestrator.register_testbed(campus_config)
    orchestrator.register_testbed(city_config)
    
    print("✓ Physical testbed preparation initialized")
    print(f"  • Available testbed templates: {len(orchestrator.active_testbeds)}")
    
    return orchestrator

def generate_deployment_ready_configurations(output_dir: str = "results/testbed_deployments"):
    """Generate deployment-ready configurations for all testbed types"""
    orchestrator = initialize_physical_testbed_preparation()
    
    print(f"\n📋 Generating deployment configurations...")
    
    for testbed_id in orchestrator.active_testbeds.keys():
        print(f"\nProcessing testbed: {testbed_id}")
        
        # Validate configuration
        validation = orchestrator.validate_testbed_configuration(orchestrator.active_testbeds[testbed_id])
        print(f"  • Validation: {'✓ PASSED' if validation['valid'] else '❌ FAILED'}")
        if validation['warnings']:
            print(f"  • Warnings: {len(validation['warnings'])}")
        if validation['errors']:
            print(f"  • Errors: {len(validation['errors'])}")
        
        # Save configurations
        orchestrator.save_testbed_configuration(testbed_id, output_dir)
    
    print(f"\n✅ All testbed configurations generated in {output_dir}/")

if __name__ == "__main__":
    print("🧪 Testing Physical Testbed Preparation...")
    
    # Test testbed generation and validation
    generate_deployment_ready_configurations()
    
    print("\n✅ Physical testbed preparation test completed!")
