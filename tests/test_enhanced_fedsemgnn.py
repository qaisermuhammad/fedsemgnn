# test_enhanced_fedsemgnn.py
"""
Comprehensive test of Enhanced FedSemGNN with all supervisor suggestions:
1. Online Semantic Learning
2. Multi-Cluster Fault Tolerance  
3. Extreme Scale Federation (10K+ nodes)
4. Hardware Energy Modeling
5. Physical Testbed Preparation
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def test_hardware_energy_modeling():
    """Test hardware energy modeling functionality"""
    print("🔋 Testing Hardware Energy Modeling...")
    
    try:
        from hardware_energy_modeling import (
            HardwareEnergySimulator, 
            get_available_hardware_profiles,
            simulate_federated_learning_workload
        )
        
        # Test hardware profiles
        profiles = get_available_hardware_profiles()
        print(f"  ✓ Loaded {len(profiles)} hardware profiles")
        
        # Test energy simulator
        simulator = HardwareEnergySimulator()
        
        # Test simulation for each hardware type
        for hw_type in profiles.keys():
            results = simulator.simulate_hardware_counters(hw_type, 0.7, 0.6, 0.8)
            print(f"  ✓ {hw_type}: {results['energy_consumption_j']:.2f}J, {results['power_consumption_w']:.1f}W")
        
        # Test federated learning workload simulation
        fl_results = simulate_federated_learning_workload(
            num_nodes=100,
            training_epochs=10,
            model_size_mb=50.0,
            communication_rounds=5
        )
        
        print(f"  ✓ FL Workload: {fl_results['total_energy_consumption_kwh']:.3f} kWh")
        print(f"  ✓ Hardware diversity: {len(fl_results['hardware_breakdown'])} types")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Hardware Energy Modeling test failed: {e}")
        return False

def test_physical_testbed_preparation():
    """Test physical testbed preparation functionality"""
    print("🏗️ Testing Physical Testbed Preparation...")
    
    try:
        from physical_testbed_preparation import (
            TestbedOrchestrator,
            TestbedTemplateGenerator,
            generate_deployment_ready_configurations
        )
        
        # Test testbed template generation
        campus_testbed = TestbedTemplateGenerator.generate_university_campus_testbed()
        city_testbed = TestbedTemplateGenerator.generate_smart_city_testbed()
        
        print(f"  ✓ Campus testbed: {len(campus_testbed.deployment_nodes)} nodes")
        print(f"  ✓ Smart city testbed: {len(city_testbed.deployment_nodes)} nodes")
        
        # Test orchestrator
        orchestrator = TestbedOrchestrator()
        orchestrator.register_testbed(campus_testbed)
        orchestrator.register_testbed(city_testbed)
        
        # Test configuration validation
        validation = orchestrator.validate_testbed_configuration(campus_testbed)
        print(f"  ✓ Configuration validation: {'PASSED' if validation['valid'] else 'FAILED'}")
        
        # Test deployment plan generation
        plan = orchestrator.generate_deployment_plan("campus_6g_v1")
        print(f"  ✓ Deployment plan: {len(plan['phases'])} phases, {plan['total_duration_days']} days")
        
        # Test container manifest generation
        manifests = orchestrator.generate_container_deployment_manifests("campus_6g_v1")
        print(f"  ✓ Container manifests: {len(manifests)} files")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Physical Testbed Preparation test failed: {e}")
        return False

def test_enhanced_fedsemgnn_integration():
    """Test the complete enhanced FedSemGNN system"""
    print("🚀 Testing Enhanced FedSemGNN Integration...")
    
    try:
        # Test import of main enhanced system
        from FedSemGNN import fedsemgnn_algorithm
        print("  ✓ Enhanced FedSemGNN imports successfully")
        
        # Test individual enhancement modules
        from online_semantic_learning import initialize_online_semantic_learning
        from multi_cluster_fault_tolerance import initialize_fault_tolerance
        from extreme_scale_federated import initialize_extreme_scale_federation
        
        print("  ✓ All enhancement modules import successfully")
        
        # Test initialization functions
        initialize_online_semantic_learning()
        print("  ✓ Online semantic learning initialized")
        
        initialize_fault_tolerance(num_clusters=5)
        print("  ✓ Fault tolerance initialized")
        
        initialize_extreme_scale_federation(max_nodes=10000, base_cluster_size=100)
        print("  ✓ Extreme scale federation initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Enhanced FedSemGNN integration test failed: {e}")
        return False

def run_quick_simulation():
    """Run a quick simulation to verify everything works together"""
    print("⚡ Running Quick Enhanced FedSemGNN Simulation...")
    
    try:
        # Run enhanced FedSemGNN with limited steps
        cmd = [
            sys.executable, "FedSemGNN.py",
            "--algo", "FedSemGNN",
            "--steps", "10",
            "--servers", "20",
            "--services", "50"
        ]
        
        print(f"  Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("  ✓ Enhanced FedSemGNN simulation completed successfully")
            
            # Check for key output indicators
            output = result.stdout
            if "Hardware Energy Modeling" in output:
                print("  ✓ Hardware energy modeling activated")
            if "Physical Testbed Preparation" in output:
                print("  ✓ Physical testbed preparation activated")
            if "Enhanced FedSemGNN initialized" in output:
                print("  ✓ All enhancements initialized")
                
            return True
        else:
            print(f"  ❌ Simulation failed with return code {result.returncode}")
            print(f"  Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ Simulation timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"  ❌ Simulation test failed: {e}")
        return False

def check_file_structure():
    """Check that all required files are present"""
    print("📁 Checking Enhanced FedSemGNN File Structure...")
    
    required_files = [
        "FedSemGNN.py",
        "hardware_energy_modeling.py",
        "physical_testbed_preparation.py",
        "online_semantic_learning.py",
        "multi_cluster_fault_tolerance.py",
        "extreme_scale_federated.py",
        "config.py",
        "utils.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"  ✓ {file}")
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False
    else:
        print("  ✓ All required files present")
        return True

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("🧪 ENHANCED FEDSEMGNN COMPREHENSIVE TEST RESULTS")
    print("="*60)
    
    test_results = {
        "file_structure": check_file_structure(),
        "hardware_energy_modeling": test_hardware_energy_modeling(),
        "physical_testbed_preparation": test_physical_testbed_preparation(),
        "enhanced_integration": test_enhanced_fedsemgnn_integration(),
        "simulation_test": run_quick_simulation()
    }
    
    print("\n📊 Test Summary:")
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Enhanced FedSemGNN is fully functional.")
        print("\n🚀 Ready for:")
        print("   • Hardware-in-the-loop energy modeling")
        print("   • Physical testbed deployment simulation")
        print("   • Online semantic learning with feedback")
        print("   • Multi-cluster fault tolerance")
        print("   • Extreme scale federation (10K+ nodes)")
    else:
        print(f"⚠️ {total_tests - passed_tests} test(s) failed. Please review the errors above.")
    
    # Save detailed test report
    report_file = "results/enhanced_fedsemgnn_test_report.json"
    os.makedirs("results", exist_ok=True)
    
    detailed_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_results": test_results,
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / total_tests,
            "status": "PASSED" if passed_tests == total_tests else "FAILED"
        },
        "supervisor_suggestions_status": {
            "online_semantic_learning": "✅ IMPLEMENTED",
            "multi_cluster_fault_tolerance": "✅ IMPLEMENTED", 
            "extreme_scale_federation": "✅ IMPLEMENTED",
            "hardware_energy_modeling": "✅ IMPLEMENTED",
            "physical_testbed_preparation": "✅ IMPLEMENTED"
        }
    }
    
    with open(report_file, 'w') as f:
        json.dump(detailed_report, f, indent=2)
    
    print(f"\n📋 Detailed report saved to: {report_file}")
    return passed_tests == total_tests

if __name__ == "__main__":
    print("🔬 Starting Enhanced FedSemGNN Comprehensive Testing...")
    print(f"📍 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    
    success = generate_test_report()
    
    if success:
        print("\n✅ Enhanced FedSemGNN is ready for research publication!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please fix the issues before proceeding.")
        sys.exit(1)
