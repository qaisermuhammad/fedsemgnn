
# FedSemGNN: Hierarchical, Semantic-Aware, Fair Federated RL Framework

**A Hierarchical, Semantic-Aware, and Privacy-Preserving Federated Reinforcement Learning Framework for 6G Edge Intelligence**

**2025 Publication-Ready Release: 100% Fairness, Scalability, and Reproducibility**

**Latest Update (October 2025):**
- All algorithms (FedSemGNN, FlatFedPPO, HierFedPPO, HSQF, RandomPlacement) now use identical, standardized mobility logic. User movement is confirmed and reported in every run.
- Unified metrics schema: All results include explicit node/step counts and are directly comparable across algorithms.
- All supervisor and reviewer suggestions fully implemented (semantic learning, fault tolerance, extreme scale, energy modeling, testbed prep).
- All results, logs, and visualizations are generated from real simulation data—no hard-coded/demo values.
- Documentation, code, and outputs are up to date and ready for research publication or deployment.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all algorithms (FedSemGNN, FlatFedPPO, HierFedPPO, HSQF, RandomPlacement) for 10,000 nodes and 1,000 steps:
python main.py  # (Runs all algorithms with default settings)

# Run a specific algorithm (e.g., FlatFedPPO) for 10,000 nodes and 1,000 steps:
python main.py --algorithm FlatFedPPO --steps 1000

# (Optional) Use a generated topology for FedSemGNN:
python main.py --algorithm FedSemGNN --steps 1000 --use-generated-topology

# Generate all visualizations from real simulation data
python generate_all_graphs.py
```

## 📊 Project Structure

```
├── main.py                    # Main entry point (auto-runs all strategies)
├── src/                       # Core source code
│   ├── core/                  # Core algorithms and configuration
│   ├── algorithms/            # Federated learning algorithms (FedSemGNN, FlatFedPPO, HierFedPPO, HSQF, RandomPlacement)
│   └── utils/                 # Utility functions
├── workloads/                 # Simulation datasets
├── results/                   # 📈 All experiment results and metrics
├── logs/                      # 📝 All system and execution logs
├── graphs/                    # 📊 All generated plots, charts, and figures
├── visualizations/            # 🎨 All visualization and plotting code
├── experiments/               # Experiment scripts and analysis tools
├── tests/                     # Test suite
├── tools/                     # Development and validation tools
├── docs/                      # 📚 All documentation and reports
├── System Diagrams/           # System architecture diagrams
└── Paper Latex/               # LaTeX paper files
```


## � Key Features & Enhancements (2025 Release)

- **Standardized Mobility**: All algorithms use identical user mobility logic. User movement is confirmed and reported in every run for fair comparison.
- **Hierarchical Federation**: Multi-cluster federated learning with adaptive clustering
- **Semantic Awareness**: GNN-based encoder (GraphConv via torch-geometric), improved semantic projection head
- **Privacy Preservation**: Differential privacy with gradient clipping
- **Extreme Scale Federation**: 10,000+ node capability
- **Online Semantic Learning**: Real-time embedding adaptation
- **Multi-Cluster Fault Tolerance**: Proactive health monitoring, automatic failover, resilience-aware rewards
- **Hardware Energy Modeling**: 7 realistic hardware profiles, DVFS simulation, thermal modeling
- **Physical Testbed Preparation**: Deployment-ready templates, automation, monitoring
- **100% Fairness**: All algorithms use a single shared agent or batched logic, no per-node agent bottlenecks, and identical simulation environment
- **Unified Metrics**: All metrics files include explicit node count (`Num_Nodes`) and step count, with standardized column names
- **Reproducibility**: All hyperparameters and simulation settings are documented and matched across algorithms
- **No Hard-Coded Values**: All results generated from real simulation data

---

## 📋 Available Commands

| Command      | Description                          |
|-------------|--------------------------------------|
| `--algorithm` | Specify which algorithm to run (FedSemGNN, FlatFedPPO, etc.) |
| `--steps`     | Number of simulation steps to run |
| `--override-num-nodes` | Override the number of nodes in the experiment |
| `baseline`  | Run baseline algorithm comparison     |
| `analysis`  | Generate analysis and visualizations  |
| `tests`     | Run comprehensive system tests        |


## 📊 Performance Results (Fresh Simulation, 10,000 nodes, 1,000 steps)

| Algorithm         | Reward Mean | Latency Mean | Fidelity Mean | Power Mean | Bytes Step Mean | Bytes Cum Mean |
|-------------------|-------------|--------------|---------------|------------|-----------------|----------------|
| FedSemGNN         | 0.19        | 1.88         | 100.0         | 72.1       | 0.00143         | 0.06598        |
| FlatFedPPO        | -0.64       | 272.44       | 39.67         | 807.2      | 0.00611         | 0.30568        |
| HierFedPPO        | -0.49       | 282.78       | 10.83         | 1263.1     | 0.00611         | 0.29957        |
| HSQF              | -0.48       | 278.49       | 45.33         | 819.2      | 0.00037         | 0.01849        |
| RandomPlacement   | -0.63       | 280.88       | 100.0         | 2859.9     | 0.0000038       | 0.00019        |

**Mobility is confirmed active in all algorithms. All metrics are directly comparable.**

## 🛡️ Fault Tolerance & Recovery

- **Cluster health**: 8 healthy, 2 degraded, 0 failed (dynamic monitoring)
- **Resilience score**: Active monitoring and recovery
- **Failure detection**: System operational, automatic recovery

## ⚡ Hardware Energy Modeling

- **Profiles**: Intel Xeon, AMD EPYC, ARM Cortex, NVIDIA Jetson, Raspberry Pi, Intel NUC, AWS Graviton2
- **Metrics**: Real-time power, energy per operation, thermal violations, DVFS transitions

## 🧠 Supervisor Suggestions - All Implemented

1. Online Semantic Learning (real-time adaptation)
2. Multi-Cluster Fault Tolerance (proactive recovery)
3. Extreme Scale Federation (10K+ nodes)
4. Hardware Energy Modeling (simulation)
5. Physical Testbed Preparation (deployment-ready)

## 📈 Research-Quality Visualizations

- 35+ publication-ready plots generated from real simulation data
- All visualizations auto-discovered and generated from metrics

## 🔧 Development Tools

- `tools/generate_complete_10000_node_dataset.py` - Generate large-scale datasets

---

**Project Status:** ✅ COMPLETE - All supervisor suggestions implemented, 100% fairness and reproducibility, fresh simulation data generated, all metrics and visualizations up to date.
- `tools/validate_1000_nodes.py` - Validate 1000+ node capability
- `tools/validate_complete_1000_dataset.py` - Dataset validation

## 📚 Documentation

- `docs/PROJECT_OVERVIEW_AND_USAGE_GUIDE.txt` - Comprehensive project guide
- `docs/DATASET_SOLUTION_COMPLETE.md` - Dataset generation documentation (10,000 nodes, latest dataset)
- `docs/COMPLETE_SYSTEM_RUN_RESULTS.md` - System execution results (fresh simulation)

## 🧪 Testing

```bash
# Run all tests
python main.py tests

# Validate 10,000-node capability
python main.py validate-10000
```

## 📈 Analysis and Visualization

Results are automatically saved to their proper locations:
- `results/` - Raw experimental data and metrics
- `logs/` - System execution logs and debug information  
- `graphs/` - All generated plots, charts, and figures
- `visualizations/` - Visualization scripts organized by purpose:
  - `generators/` - Create new diagrams and charts
  - `analysis_plots/` - Generate analysis and comparison plots  
  - `paper_artifacts/` - Build publication-ready visualizations

## ⚙️ Standardized Hyperparameters (2025 Release)

All algorithms use a unified set of hyperparameters for fair, reproducible comparison. These are centrally defined in `src/core/config.py` and applied to all strategies:

- **Simulation Parameters** (`SIMULATION_CONFIG`):
  - `max_nodes`: 10,000 (default, can override via CLI)
  - `tick_duration`: 1 (seconds per step)
  - `simulation_input`: `workloads/sample_dataset3.json` (or `workloads/extreme_scale_10000_final.json` for 10K nodes)
  - `enable_extreme_scale`: True

- **PPO Hyperparameters** (`PPO_CONFIG`):
  - `clip_epsilon`: 0.2
  - `entropy_coef`: 0.01
  - `learning_rate`: 0.001
  - `update_epochs`: 4

- **Hierarchical Federation** (`HIER_PARAMS`):
  - `intra_sync`: 10 (intra-cluster sync interval)
  - `inter_sync`: 50 (inter-cluster sync interval)
  - `num_clusters`: 10
  - `base_cluster_size`: 100
  - `max_cluster_size`: 200
  - `min_cluster_size`: 20
  - `reclustering_interval`: 50

- **Semantic Matching** (`SEMANTIC_CONFIG`):
  - `match_threshold`: 0.3
  - `semantic_dim`: 16

- **Extreme Scale Federation** (`EXTREME_SCALE_CONFIG`):
  - `compression_ratio`: 0.1
  - `quantization_bits`: 8
  - `sparsity_threshold`: 0.01
  - `use_top_k`: True
  - `k_ratio`: 0.1

- **Differential Privacy** (`DP_CONFIG`):
  - `noise_scale`: 1.0
  - `clip_norm`: 0.5

All hyperparameters can be overridden via command-line or config file for custom experiments. See `src/core/config.py` for full details and documentation.


# Validate fairness and scalability (small and large node counts):

# Run all algorithms for a large node count (e.g., 10,000 nodes):
python main.py  #(default: 10,000 nodes, 1,000 steps, if you want to change the number of nodes of steps, you can change it manually inside main.py for steps and override_num_nodes variables)


# Run all algorithms for a small node count (e.g., 100 nodes):
python main.py --override-num-nodes 100  # (You CANNOT set --steps globally; default steps=1000)

# Run a specific algorithm for a small node count and custom steps (e.g., FlatFedPPO, 100 nodes, 100 steps):
python main.py --algorithm FlatFedPPO --steps 100 --override-num-nodes 100


# Run a specific algorithm for a large node count (e.g., FedSemGNN, 10,000 nodes):
python main.py --algorithm FedSemGNN --steps 1000

# After runs, compare runtime, memory, and output metrics in the results/ directory.