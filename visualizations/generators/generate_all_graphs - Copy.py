#!/usr/bin/env python3
"""
Unified script to generate ALL FedSemGNN diagrams and metrics graphs in a single run.
All outputs are saved directly in the 'graphs' folder.
"""
import sys
import os
from pathlib import Path
import subprocess

# Ensure output directory exists
graphs_dir = Path("graphs")
graphs_dir.mkdir(exist_ok=True)

# List of all generator scripts to run
def get_generator_scripts():
    folder = Path(__file__).parent
    exclude = {"generate_all_graphs.py", "consolidated_diagrams.py", "hardware_energy_modeling_individual.py", "generate_strategy_table.py"}
    return [f.name for f in folder.glob("*.py") if f.name not in exclude]

scripts = get_generator_scripts()

def run_script(script_name):
    print(f"\n🔄 Running {script_name}...")
    if not os.path.exists(script_name):
        print(f"⚠️  Script not found: {script_name}")
        return False
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {script_name} completed successfully.")
        if result.stdout:
            print(result.stdout.strip())
        return True
    else:
        print(f"❌ Error running {script_name}:")
        if result.stderr:
            print(result.stderr.strip())
        return False

def main():
    print("\n🚀 FedSemGNN Unified Graph Generator")
    print("=" * 60)
    success = 0
    for script in scripts:
        if run_script(script):
            success += 1
    print(f"\n✅ Completed {success}/{len(scripts)} scripts.")
    print(f"All graphs are saved in: {graphs_dir.resolve()}")

if __name__ == "__main__":
    main()
