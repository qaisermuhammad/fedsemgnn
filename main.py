import sys
import os
import argparse
from typing import Dict, Any

# Add src to path for imports
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def _script_supports_flag(script_path: str, flag: str) -> bool:
    """Best-effort guard to avoid passing unsupported CLI flags to scripts."""
    try:
        with open(script_path, "r", encoding="utf-8", errors="ignore") as f:
            # Read only the first chunk; enough to catch argparse declarations.
            chunk = f.read(200_000)
        return flag in chunk
    except Exception:
        return False


def main():
    """Main entry point with command-line interface."""
    import sys
    parser = argparse.ArgumentParser(
        description="FedSemGNN: Hierarchical, Semantic-Aware Federated RL Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
            python main.py setup                  # Initialize project
            python main.py experiment             # Run FedSemGNN experiment
            python main.py baseline               # Run baseline comparisons
            python main.py analysis               # Generate analysis and plots
            python main.py tests                  # Run system tests
            python main.py paper                  # Generate paper artifacts
        """
    )
    # Always use 1000 nodes and sample_dataset3.json for all runs
    # This does NOT modify or overwrite your dataset. A temporary file is used for the run.
    # 6G Edge Server Scalability Research Parameters
    #   python main.py --override-num-nodes 1000 --use-generated-topology --topology-mode random --topology-degree 8 --6g-edge-mode
    parser.add_argument('--use-generated-topology', action='store_true', help='Use a programmatically generated scalable topology (does not modify dataset)')
    parser.add_argument('--topology-mode', default='ring', choices=['ring', 'random', 'smallworld'], help='Topology type for generated topology (ring, random, smallworld)')
    parser.add_argument('--topology-degree', type=int, default=4, help='Degree/avg_degree/k for generated topology (controls connectivity)')
    parser.add_argument('--override-num-nodes', type=int, default=1000, help='Override the number of nodes (default: 1000)')
    
    # 6G Edge Server Research Configuration
    parser.add_argument('--6g-edge-mode', action='store_true', help='Enable 6G edge server power scaling model for research')
    parser.add_argument('--edge-server-load', type=float, default=0.7, help='Edge server load factor (0.0-1.0, default: 0.7)')
    parser.add_argument('--deployment-scenario', choices=['smart_city', 'metropolitan', 'national'], 
                       help='6G deployment scenario for research analysis')
    parser.add_argument('--power-model-config', type=str, help='Path to custom 6G power model configuration file')
    parser.add_argument('--research-output-dir', type=str, default='results/6g_research', 
                       help='Output directory for 6G research results')
    # Remove all subparsers and subcommands; CLI is now flat
    
    # Remove experiment subcommand; all arguments are now global
    parser.add_argument('--steps', type=int, default=1000, help='Number of simulation steps (default: 1000 for final experiment)')
    parser.add_argument('--algorithm', 
                       choices=['FedSemGNN', 'FlatFedPPO', 'CentralizedPPO', 'HierFedPPO', 'HSQF', 'RandomPlacement'],
                       help='Algorithm to run (if omitted, runs all algorithms)')
    parser.add_argument('--encoder', default='gnn', choices=['gnn', 'linear'], help='Encoder type for FedSemGNN (gnn=GraphConv, linear=MLP)')
    parser.add_argument('--config-override', type=str, default=None, help='Path to JSON file with hyperparameter overrides (forwarded to algorithm scripts that support it)')

    
    parser.add_argument('--tune', action='store_true', help='Run fair hyperparameter tuning for all algorithms')
    args = parser.parse_args()

    # --- Fair Hyperparameter Tuning Command ---
    if getattr(args, 'tune', False):
        import itertools, subprocess, json
        # Shared search space for all algorithms (reduced grid for quick test run)
        learning_rates = [1e-3]
        sync_intervals = [5]
        smoothing_windows = [10]
        entropy_coefs = [0.01]
        # For FedSemGNN only
        dropout_rates = [0.0]
        algorithms = ["FedSemGNN", "FlatFedPPO", "CentralizedPPO", "HierFedPPO", "HSQF", "RandomPlacement"]
        algo_scripts = {
            "FedSemGNN": os.path.join("src", "algorithms", "FedSemGNN.py"),
            "FlatFedPPO": os.path.join("src", "algorithms", "flat_fedppo.py"),
            "CentralizedPPO": os.path.join("src", "algorithms", "centralized_ppo.py"),
            "HierFedPPO": os.path.join("src", "algorithms", "hier_fedppo.py"),
            "HSQF": os.path.join("src", "algorithms", "hsqf.py"),
            "RandomPlacement": os.path.join("src", "algorithms", "random_place.py"),
        }
        # Map algorithm to actual output metrics filename
        metrics_filenames = {
            "FedSemGNN": "fedsemgnn_metrics.csv",
            "FlatFedPPO": "flat_fedppo_metrics.csv",
            "CentralizedPPO": "centralized_ppo_metrics.csv",
            "HierFedPPO": "hier_fedppo_metrics.csv",
            "HSQF": "hsqf_metrics.csv",
            "RandomPlacement": "random_place_metrics.csv",
        }
        steps = 100
        results_dir = "results/tuning/"
        os.makedirs(results_dir, exist_ok=True)
        # Grid search (fair for all)
        for algo in algorithms:
            print(f"[TUNE] {algo}")
            # Use dropout only for FedSemGNN
            if algo == "FedSemGNN":
                grid = itertools.product(learning_rates, sync_intervals, smoothing_windows, entropy_coefs, dropout_rates)
            else:
                grid = itertools.product(learning_rates, sync_intervals, smoothing_windows, entropy_coefs)
            for idx, params in enumerate(grid):
                # Unpack params
                lr, sync, smooth, entropy = params[:4]
                dropout = params[4] if algo == "FedSemGNN" else None
                # Prepare config override as JSON
                config_override = {
                    "learning_rate": lr,
                    "sync_interval": sync,
                    "smoothing_window": smooth,
                    "entropy_coef": entropy
                }
                if dropout is not None:
                    config_override["dropout"] = dropout
                config_path = os.path.join(results_dir, f"{algo}_config_{idx}.json")
                with open(config_path, "w") as f:
                    json.dump(config_override, f)
                # Remove old metrics file
                metrics_path = os.path.join("results", metrics_filenames[algo])
                if os.path.exists(metrics_path):
                    try:
                        os.remove(metrics_path)
                    except Exception:
                        pass
                # Build command
                script = algo_scripts[algo]
                cmd = [sys.executable, script, "--steps", str(steps), "--config-override", config_path]
                print(f"[TUNE] Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
                # Save/rename metrics file for this run
                if os.path.exists(metrics_path):
                    run_metrics = os.path.join(results_dir, f"{algo}_metrics_{idx}.csv")
                    # Remove destination if it exists to avoid FileExistsError
                    if os.path.exists(run_metrics):
                        os.remove(run_metrics)
                    os.rename(metrics_path, run_metrics)
                else:
                    print(f"[TUNE][WARNING] Metrics file not found for {algo} run {idx}: {metrics_path}")
                print(f"[TUNE] {algo} run {idx} complete.")
        print("[TUNE] All tuning runs complete! Results in results/tuning/")
        return

    # Remove all subcommand logic; always run based on global arguments
    
    # 6G Edge Server Research Configuration Setup
    if getattr(args, '6g_edge_mode', False):
        print("[6G RESEARCH] Enabling 6G Edge Server Power Scaling Model")
        
        # Setup 6G research output directory
        research_dir = getattr(args, 'research_output_dir', 'results/6g_research')
        os.makedirs(research_dir, exist_ok=True)
        
        # Initialize 6G power model
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from power_model.edge_6g_power import EdgeServerPowerModel
        
        power_model = EdgeServerPowerModel()
        
        # Load custom configuration if provided
        if getattr(args, 'power_model_config', None):
            power_model.load_config(args.power_model_config)
            print(f"[6G RESEARCH] Loaded custom power model config: {args.power_model_config}")
        
        # Set research context in environment for algorithms to use
        os.environ['FEDSEMGNN_6G_MODE'] = 'true'
        os.environ['FEDSEMGNN_EDGE_LOAD'] = str(getattr(args, 'edge_server_load', 0.7))
        os.environ['FEDSEMGNN_RESEARCH_DIR'] = research_dir
        
        # Save power model configuration for this run
        config_file = os.path.join(research_dir, '6g_power_model_config.json')
        power_model.save_config(config_file)
        print(f"[6G RESEARCH] Power model config saved to: {config_file}")
        
        # Log research context
        deployment_scenario = getattr(args, 'deployment_scenario', None)
        if deployment_scenario:
            print(f"[6G RESEARCH] Deployment scenario: {deployment_scenario}")
        
        override_num_nodes = getattr(args, 'override_num_nodes', 1000)
        print(f"[6G RESEARCH] Node count: {override_num_nodes}")
        print(f"[6G RESEARCH] Edge server load factor: {getattr(args, 'edge_server_load', 0.7)}")
    
    # If no algorithm is specified, run all algorithms
    if not getattr(args, 'algorithm', None):
        import subprocess
        algo_scripts = {
            "FedSemGNN": os.path.join("src", "algorithms", "FedSemGNN.py"),
            "FlatFedPPO": os.path.join("src", "algorithms", "flat_fedppo.py"),
            "CentralizedPPO": os.path.join("src", "algorithms", "centralized_ppo.py"),
            "HierFedPPO": os.path.join("src", "algorithms", "hier_fedppo.py"),
            "HSQF": os.path.join("src", "algorithms", "hsqf.py"),
            "RandomPlacement": os.path.join("src", "algorithms", "random_place.py"),
        }
        algorithms = list(algo_scripts.keys())
        steps = getattr(args, 'steps', 1000)
        override_num_nodes = getattr(args, 'override_num_nodes', 1000)
        print(f"[INFO] Running ALL algorithms for {override_num_nodes} nodes, {steps} steps, using workloads/sample_dataset3.json")
        for algo in algorithms:
            print(f"Running {algo}...")
            metrics_map = {
                "FedSemGNN": "results/fedsemgnn_metrics.csv",
                "FlatFedPPO": "results/flat_fedppo_metrics.csv",
                "CentralizedPPO": "results/centralized_ppo_metrics.csv",
                "HierFedPPO": "results/hier_fedppo_metrics.csv",
                "HSQF": "results/hsqf_metrics.csv",
                "RandomPlacement": "results/random_place_metrics.csv",
            }
            metrics_path = metrics_map.get(algo, f"results/{algo}_metrics.csv")
            if os.path.exists(metrics_path):
                try:
                    os.remove(metrics_path)
                    print(f"Deleted old metrics file: {metrics_path}")
                except Exception as e:
                    print(f"Warning: Could not delete {metrics_path}: {e}")
            script = algo_scripts[algo]
            cmd = [
                sys.executable,
                script,
                "--steps", str(steps),
                "--override-num-nodes", str(override_num_nodes)
            ]
            if getattr(args, 'config_override', None):
                script_abs = os.path.join(os.path.dirname(__file__), script)
                if _script_supports_flag(script_abs, "--config-override"):
                    cmd.extend(["--config-override", str(getattr(args, 'config_override'))])
                else:
                    print(f"[INFO] Skipping --config-override for {algo} (script does not declare it): {script}")
            
            # Add 6G research parameters if enabled
            if getattr(args, '6g_edge_mode', False):
                cmd.extend(["--6g-edge-mode"])
                cmd.extend(["--edge-server-load", str(getattr(args, 'edge_server_load', 0.7))])
            
            # Add topology parameters if specified
            if getattr(args, 'use_generated_topology', False):
                cmd.extend(["--use-generated-topology"])
                cmd.extend(["--topology-mode", getattr(args, 'topology_mode', 'ring')])
                cmd.extend(["--topology-degree", str(getattr(args, 'topology_degree', 4))])
            # Ensure we use the same environment
            env = os.environ.copy()
            result = subprocess.run(cmd, cwd=os.path.dirname(__file__), capture_output=True, text=True, env=env)
            if result.returncode == 0:
                print(f"{algo} completed successfully")
            else:
                print(f"{algo} failed (return code {result.returncode})")
                print("--- STDOUT ---")
                print(result.stdout)
                print("--- STDERR ---")
                print(result.stderr)
            if not os.path.exists(metrics_path):
                print(f"WARNING: Metrics file missing for {algo}: {metrics_path}")
            else:
                print(f"Metrics file found for {algo}: {metrics_path}")
        print("All algorithms complete!")
        return
    # Remove experiment subcommand logic; all runs are now handled by global arguments
    # If an algorithm is specified, run only that algorithm
    if getattr(args, 'algorithm', None):
        algo_scripts = {
            "FedSemGNN": os.path.join("src", "algorithms", "FedSemGNN.py"),
            "FlatFedPPO": os.path.join("src", "algorithms", "flat_fedppo.py"),
            "CentralizedPPO": os.path.join("src", "algorithms", "centralized_ppo.py"),
            "HierFedPPO": os.path.join("src", "algorithms", "hier_fedppo.py"),
            "HSQF": os.path.join("src", "algorithms", "hsqf.py"),
            "RandomPlacement": os.path.join("src", "algorithms", "random_place.py"),
        }
        algo = getattr(args, 'algorithm', 'FedSemGNN')
        encoder = getattr(args, 'encoder', 'gnn')
        script = algo_scripts.get(algo, algo_scripts["FedSemGNN"])
        steps = getattr(args, 'steps', 1000)
        override_num_nodes = getattr(args, 'override_num_nodes', 1000)
        import subprocess
        # --- Mobility Model Setup for Reproducibility ---
        # Mobility model setup is now handled inside each algorithm script for correctness.
        # --- End Mobility Model Setup ---
        cmd = [
            sys.executable,
            script,
            "--steps", str(steps),
            "--override-num-nodes", str(override_num_nodes)
        ]
        if getattr(args, 'config_override', None):
            script_abs = os.path.join(os.path.dirname(__file__), script)
            if _script_supports_flag(script_abs, "--config-override"):
                cmd.extend(["--config-override", str(getattr(args, 'config_override'))])
            else:
                print(f"[INFO] Skipping --config-override for {algo} (script does not declare it): {script}")
        if getattr(args, 'use_generated_topology', False):
            cmd += ["--use-generated-topology"]
            cmd += ["--topology-mode", str(getattr(args, 'topology_mode', 'ring'))]
            cmd += ["--topology-degree", str(getattr(args, 'topology_degree', 4))]
        print(f"Executing: {' '.join(cmd)}")
        # Ensure we use the same environment
        env = os.environ.copy()
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__), env=env)
        if result.returncode == 0:
            print(f"{algo} run completed successfully!")
            print("Results saved to results/ directory")
        else:
            print(f"{algo} run failed with return code: {result.returncode}")
        return


if __name__ == "__main__":
    main()