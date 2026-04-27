#!/usr/bin/env python3
"""
Master Script to Generate All Individual System Diagrams
Runs all individual diagram generators for FedSemGNN research
"""

import subprocess
import sys
import os
import time

def run_script(script_name):
    """Run a Python script and capture output"""
    try:
        print(f"\n🔄 Running {script_name}...")
        start_time = time.time()
        
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ {script_name} completed successfully in {duration:.2f}s")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}:")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error running {script_name}: {e}")
        return False

def main():
    """Generate all individual system diagrams"""
    print("🚀 FedSemGNN Individual System Diagrams Generator")
    print("=" * 60)
    
    # List of individual diagram scripts to run
    diagram_scripts = [
        "convergence_analysis_individual.py",
        "scalability_analysis_individual.py", 
        "fault_tolerance_metrics_individual.py",
        "semantic_learning_analysis_individual.py",
        "temporal_performance_analysis_individual.py",
        "hardware_energy_modeling_individual.py"
    ]
    
    # Also run existing individual comparison scripts
    comparison_scripts = [
        "placement_accuracy_comparison.py",
        "latency_comparison.py",
        "energy_comparison.py", 
        "communication_overhead_comparison.py"
    ]
    
    all_scripts = diagram_scripts + comparison_scripts
    
    print(f"📋 Total scripts to run: {len(all_scripts)}")
    print(f"📁 Output directory: graphs/")
    print("-" * 60)
    
    # Track results
    successful = []
    failed = []
    total_start_time = time.time()
    
    # Run each script
    for script in all_scripts:
        if os.path.exists(script):
            if run_script(script):
                successful.append(script)
            else:
                failed.append(script)
        else:
            print(f"⚠️  Script not found: {script}")
            failed.append(script)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 GENERATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully generated: {len(successful)} diagrams")
    print(f"❌ Failed: {len(failed)} diagrams")
    print(f"⏱️  Total time: {total_duration:.2f} seconds")
    
    if successful:
        print(f"\n✅ Successfully generated diagrams:")
        for script in successful:
            print(f"   • {script}")
    
    if failed:
        print(f"\n❌ Failed to generate:")
        for script in failed:
            print(f"   • {script}")
    
    # Check output directory
    output_dir = "graphs"
    if os.path.exists(output_dir):
        png_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
        total_size = sum(os.path.getsize(os.path.join(output_dir, f)) 
                        for f in png_files) / (1024 * 1024)
        
        print(f"\n📁 Output directory: {output_dir}/")
        print(f"� Generated PNG files: {len(png_files)}")
        print(f"💾 Total size: {total_size:.2f} MB")
        
        if len(png_files) > 0:
            print(f"\n📋 Generated files:")
            for f in sorted(png_files):
                file_size = os.path.getsize(os.path.join(output_dir, f)) / (1024 * 1024)
                print(f"   • {f} ({file_size:.2f} MB)")
    
    print(f"\n🎯 All individual diagrams generated successfully!")
    print(f"🔬 Ready for research paper integration!")
    
    return len(failed) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)