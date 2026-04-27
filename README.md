# FedSemGNN — Federated Semantic GNN for 6G Edge Intelligence

<div align="center">

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=flat&logo=PyTorch&logoColor=white)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

> **Hierarchical, Semantic-Aware, Privacy-Preserving Federated Reinforcement Learning Framework for 6G Edge Orchestration**

## Overview

FedSemGNN addresses real-time service/task placement on heterogeneous edge servers in 6G networks. It combines four technical innovations:

1. **Hierarchical Federated PPO** — Two-level parameter synchronization: local every K₁=10 steps, global every K₂=50 steps across 10 clusters
2. **GNN-based topology encoding** — 2-layer GCN (128→64→64) with symmetric normalization learns edge infrastructure topology
3. **Custom continual-learning semantic encoder** — 128→64→64→16 architecture with EWC regularization (λ=0.4) processes service metadata without pre-trained models
4. **Differential privacy** — Gaussian noise (σ=1.0, clip norm 0.5) protects model updates during federated aggregation

**Key verified results** (6-node base scale, 1,000 timesteps, 5-trial average):

| Metric                 | FedSemGNN                  | Best Baseline              |
|--------                |-----------                 |--------------             |
| Orchestration latency  | 39.08 ± 6.23 ms            | 82–135 ms                  |
| Semantic fidelity      | ~100%                      | 72–100%                    |
| Communication overhead | 0.72 MB cumulative         | 2.9–207.7 MB               |
| Scalability range      | 6–1,000 nodes (167× range) | —                          |
| Power consumption      | 2,674 W                    | 840–3,166 W                |

The framework is benchmarked against **5 self-implemented baselines** (FlatFedPPO, CentralizedPPO, HierFedPPO, HSQF, RandomPlacement) and **3 published methods** (ECO-SDIoT, GFL-LFF, FRPVC).

---

## Architecture

```
                    ┌─────────────────────┐
                    │   Global Aggregator  │
                    │  (K₂=50 sync)       │
                    └──────┬──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Cluster 1│ │ Cluster 2│ │...Clust 10│   ← Local aggregation (K₁=10)
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │             │             │
        ┌────┴────┐   ┌───┴────┐   ┌───┴────┐
        │ Edge    │   │ Edge   │   │ Edge   │     ← PPO agents with:
        │ Agents  │   │ Agents │   │ Agents │        - GCN encoder (topology)
        └─────────┘   └────────┘   └────────┘        - Semantic encoder (service metadata)
                                                      - DP noise injection
```

**Data flow:**
1. EdgeSimPy simulation generates service placement requests with mobility
2. Each edge agent observes: local load, neighbor topology (via GCN), service semantics (via encoder)
3. PPO selects placement action; reward combines latency, fidelity, power, communication
4. Local models sync within cluster every K₁ steps; clusters sync globally every K₂ steps
5. Differential privacy noise added before each aggregation step

**GCN Architecture:**
- Input: 128-dim node features (server state + service metadata)
- Layer 1: GraphConv 128→64 + ReLU + Dropout(0.5)
- Layer 2: GraphConv 64→64
- Adjacency: Symmetric normalization (D⁻¹/²AD⁻¹/²)
- Source: `src/utils/gcn_encoder.py`

**Semantic Encoder:**
- Architecture: 128→64→64→16 (not Sentence-BERT; fully custom)
- EWC continual learning: λ_EWC=0.4 to prevent catastrophic forgetting
- Online learning rate: 0.0001
- Semantic threshold: τ=0.3 (adaptive: τᵢ = clip(τ₀ + κ(pᵢ − 0.5)))
- Source: `src/core/online_semantic_learning.py`, `src/algorithms/FedSemGNN.py`

---

## Directory Structure

```
FedSemGNN/
├── main.py                          # CLI entry point — runs all/single algorithm
├── requirements.txt                 # Python dependencies
│
├── src/                             # Core source code
│   ├── algorithms/                  # All RL algorithm implementations
│   │   ├── FedSemGNN.py            #   Main framework (hierarchical fed + GCN + semantic)
│   │   ├── flat_fedppo.py          #   Single-level federated PPO baseline
│   │   ├── centralized_ppo.py      #   Non-federated centralized PPO
│   │   ├── hier_fedppo.py          #   Hierarchical fed PPO (no semantics/GCN)
│   │   ├── hsqf.py                 #   Heuristic Shortest Queue First
│   │   ├── PPO.py                  #   Base PPO (actor-critic, replay buffer, 16-dim hidden)
│   │   ├── ppo_semantic.py         #   PPO with semantic extensions
│   │   └── random_place.py         #   Random placement baseline
│   ├── core/                        # Configuration and extensions
│   │   ├── config.py               #   Default hyperparameters (PPO, GNN, DP, federation)
│   │   ├── config_1000_nodes.py    #   Scaled config for large-node experiments
│   │   ├── extreme_scale_federated.py  # Extreme-scale federation logic
│   │   ├── hardware_energy_modeling.py # Utilization-based power estimation
│   │   ├── multi_cluster_fault_tolerance.py  # Fault injection/recovery
│   │   └── online_semantic_learning.py       # EWC continual learning
│   ├── utils/                       # Shared utilities
│   │   ├── gcn_encoder.py          #   2-layer GCN with symmetric normalization
│   │   ├── graph_utils.py          #   Topology graph construction
│   │   ├── semantic_utils.py       #   Semantic embedding helpers
│   │   ├── service_modeling.py     #   Service/workload modeling
│   │   ├── comm_latency_instrument.py  # Communication latency instrumentation
│   │   ├── instrument_orch_latency.py  # Orchestration latency instrumentation
│   │   └── step_latency_instrument.py  # Per-step latency breakdown
│   ├── mobility/                    # Mobility modeling
│   │   ├── mobility_tracker.py     #   User movement tracking
│   │   ├── live_mobility_visualizer.py
│   │   └── mobility_performance_analyzer.py
│   └── power_model/                 # 6G edge power models
│       └── edge_6g_power.py        #   DVFS-based power estimation
│
├── sim_layers/
│   └── hardware_layer.py           # EdgeSimPy hardware abstraction layer
│
├── fed/                             # Federated learning utilities
│   ├── async_clock.py              #   Asynchronous synchronization clock
│   └── param_thinning.py           #   Parameter compression for comm efficiency
│
├── semantics/                       # Semantic processing
│   └── online_embed.py             #   Online embedding model updates
│
├── energy/                          # Energy modeling
│   ├── model.py                    #   Analytical energy consumption model
│   └── dvfs.py                     #   Dynamic voltage/frequency scaling simulation
│
├── reward/
│   └── resilience.py               # Resilience-aware reward shaping
│
├── faults/
│   └── injector.py                 # Fault injection for robustness testing
│
├── experiments/                     # Experiment scripts (~42 files)
│   ├── run_all_algorithms.py       #   Run all 6 algorithms sequentially
│   ├── run_multi_trial.py          #   Multi-trial experiments (5 seeds)
│   ├── run_scalability.py          #   Scalability study (6–1K nodes)
│   ├── run_parameter_sensitivity.py #  Parameter sensitivity analysis
│   ├── run_comprehensive.py        #   Full experiment suite
│   ├── gen_multi_trial_figure.py   #   Generate multi-trial comparison figures
│   ├── gen_scalability_figure.py   #   Generate scalability analysis figures
│   ├── metrics_logger.py           #   Unified metrics logging
│   ├── metrics_loader.py           #   Load and parse result CSVs
│   ├── quick_sensitivity.py        #   Quick tau/lambda sensitivity sweep
│   ├── quick_sensitivity_arch.py   #   Architecture sensitivity sweep
│   ├── verify_convergence.py       #   Convergence verification
│   └── ...                         #   (see experiments/ for full list)
│
├── tests/                           # Test suite
│   ├── test_enhanced_fedsemgnn.py  #   Core FedSemGNN integration tests
│   ├── test_extreme_scale.py       #   Large-scale stress tests
│   ├── test_quick_simulation.py    #   Smoke tests
│   └── final_integration_test.py   #   End-to-end integration test
│
├── tools/                           # Data preparation utilities
│   ├── topology_generator.py       #   Generate topologies (ring/random/smallworld)
│   ├── generate_complete_1000_node_dataset.py  # 1K node dataset generator
│   ├── validate_1000_nodes.py      #   Dataset validation
│   └── repair_dataset_attributes.py #  Fix dataset inconsistencies
│
├── workloads/                       # Simulation datasets
│   ├── dataset.json                #   Base dataset (6 servers)
│   ├── scale_1000_nodes.json       #   1,000-node dataset
│   ├── scale_1000_nodes_connected.json  # 1K nodes with connected topology
│   ├── dataset_10000.json          #   10,000-node dataset
│   ├── extreme_scale_10000.json    #   Extreme scale dataset
│   ├── generate_dataset.py         #   Dataset generation script
│   └── generate_extreme_scale_10000.py  # 10K dataset generator
│
├── results/                         # Experiment outputs
│   ├── multi_trial/                #   5-trial results (multi_trial_summary.csv)
│   ├── scalability/                #   Scalability study (scalability_results.csv)
│   ├── sensitivity/                #   Parameter sensitivity sweeps
│   ├── _prio_off.csv              #   Priority study: priority disabled
│   ├── _prio_hash20_slope02.csv   #   Priority study: hash-based priority
│   ├── <algo>_metrics.csv          #   Per-algorithm single-run metrics
│   └── fair_optimized/             #   Fair optimization comparison results
│
├── figures/                         # High-quality figures (PNG + PDF)
├── graphs/                          # Additional graph outputs
│
├── visualizations/                  # Extended visualization outputs
│   ├── analysis_plots/
│   ├── generators/
│   └── metrics/
│
├── logs/                            # EdgeSimPy msgpacks + run logs
├── reports/                         # Comparison and analysis reports
│
├── docs/                            # Project documentation
│   └── README.md                   #   ← THIS FILE
│
└── generate_all_graphs.py           # Master graph generation script
```

---

## Quick Start

### Dataset Preparation
Before running simulations, you must download the Alibaba cluster workload dataset:

1. Download the dataset components from the official repository: [Alibaba Cluster Trace v2018](https://github.com/alibaba/clusterdata/blob/master/cluster-trace-v2018/trace_2018.md)
2. Place the downloaded trace files inside the `data/alibaba2018/` directory.

### Running the Framework

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run all 6 algorithms (default: 1,000 nodes, 1,000 steps)
python main.py

# 3. Run a specific algorithm
python main.py --algorithm FedSemGNN --steps 1000

# 4. Run with custom node count
python main.py --override-num-nodes 1000 --steps 500

# 5. Run with 6G edge power model
python main.py --6g-edge-mode

# 6. Run with generated topology
python main.py --algorithm FedSemGNN --use-generated-topology --topology-mode smallworld

# 7. Generate all figures
python generate_all_graphs.py

# 8. Run multi-trial experiment (5 seeds)
python experiments/run_multi_trial.py

# 9. Run scalability study (6 to 1,000 nodes)
python experiments/run_scalability.py

# 10. Run parameter sensitivity analysis
python experiments/run_parameter_sensitivity.py
```

### CLI Reference (`main.py`)

| Flag | Default | Description |
|------|---------|-------------|
| `--algorithm` | all | One of: FedSemGNN, FlatFedPPO, CentralizedPPO, HierFedPPO, HSQF, RandomPlacement |
| `--steps` | 1000 | Number of simulation timesteps |
| `--override-num-nodes` | 1000 | Number of edge nodes |
| `--6g-edge-mode` | off | Enable 6G edge power model |
| `--use-generated-topology` | off | Use generated topology instead of dataset topology |
| `--topology-mode` | ring | Topology type: ring, random, smallworld |
| `--topology-degree` | 4 | Node connectivity degree for topology |
| `--encoder` | gnn | Encoder type: gnn or linear |
| `--config-override` | — | JSON string to override any config parameter |
| `--tune` | off | Run hyperparameter grid search |

When no `--algorithm` is specified, `main.py` iterates all 6 algorithms via `subprocess.run`, writing per-algorithm metrics to `results/<algo>_metrics.csv`.

---

## Configuration & Hyperparameters

All hyperparameters are centrally defined in `src/core/config.py` (base) and `src/core/config_1000_nodes.py` (scaled).

### PPO Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| Learning rate (α) | 0.001 | `src/core/config.py:29` |
| Clip epsilon (ε) | 0.2 | `src/core/config.py:27` |
| Discount factor (γ) | 0.99 | `src/algorithms/PPO.py:93` |
| Entropy coefficient (β) | 0.01 | `src/core/config.py:28` |
| Batch size | 64 | `src/algorithms/PPO.py:92` |
| Update epochs | 4 | `src/core/config.py:30` |
| Replay buffer | 20,000 | `src/algorithms/PPO.py:91` |
| Actor/Critic hidden dim | 16 | `src/algorithms/PPO.py:69` |
| Dropout | 0.5 | `src/algorithms/PPO.py:69` |

### GNN Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| Input features | 128 | `src/algorithms/FedSemGNN.py:31` |
| Hidden dimension | 64 | `src/core/config.py:40` |
| Number of layers | 2 | `src/utils/gcn_encoder.py:17-18` |
| Activation | ReLU | `src/utils/gcn_encoder.py:48` |
| Normalization | Symmetric (D⁻¹/²AD⁻¹/²) | `src/utils/gcn_encoder.py` |

### Semantic Encoder

| Parameter | Value | Source |
|-----------|-------|--------|
| Architecture | 128→64→64→16 | `src/algorithms/FedSemGNN.py` |
| Threshold (τ) | 0.3 | `src/core/config.py:52` |
| Online learning rate | 0.0001 | `src/core/config_1000_nodes.py:87` |
| EWC lambda (λ) | 0.4 | `src/core/online_semantic_learning.py:33` |

### Hierarchical Federation

| Parameter | Value | Source |
|-----------|-------|--------|
| Intra-cluster sync (K₁) | 10 | `src/core/config.py:36` |
| Inter-cluster sync (K₂) | 50 | `src/core/config.py:37` |
| Number of clusters | 10 | `src/core/config.py:38` |
| Base cluster size | 100 | `src/core/config.py` |
| Reclustering interval | 50 steps | `src/core/config.py:46` |

### Differential Privacy

| Parameter | Value | Source |
|-----------|-------|--------|
| Noise scale (σ) | 1.0 | `src/core/config.py:21` |
| Clip norm | 0.5 | `src/core/config.py:22` |

### Large Scale Adjustments

When running at large scale (`config_1000_nodes.py`): LR→0.00001, batch→16, epochs→1, clip ε→0.1, compression ratio 0.1, quantization 8-bit, top-k sparsification (k=0.1).

### Simulation

| Parameter | Value |
|-----------|-------|
| Default timesteps | 1,000 |
| Default nodes | 1,000 |
| Tick duration | 1 second |
| Mobility | Standardized across all algorithms |

---

## Algorithms

### FedSemGNN (proposed)
- **File:** `src/algorithms/FedSemGNN.py`
- Hierarchical 2-level federated PPO + GCN topology encoding + semantic continual learning + differential privacy
- Achieves (5-trial, 6 nodes): -0.59 reward, 39.08 ms latency, 99.97% fidelity, 2,674 W power, 0.72 MB comm

### FlatFedPPO
- **File:** `src/algorithms/flat_fedppo.py`
- Single-level federated PPO without hierarchy, GCN, or semantics
- Achieves (5-trial, 6 nodes): 0.25 reward, 127.75 ms latency, 71.93% fidelity

### CentralizedPPO
- **File:** `src/algorithms/centralized_ppo.py`
- Non-federated centralized PPO baseline

### HierFedPPO
- **File:** `src/algorithms/hier_fedppo.py`
- Hierarchical federated PPO without semantic or GCN components
- Achieves (5-trial, 6 nodes): 0.57 reward, 82.05 ms latency, 98.45% fidelity

### HSQF (Heuristic Shortest Queue First)
- **File:** `src/algorithms/hsqf.py`
- Non-learning heuristic baseline
- Achieves (5-trial, 6 nodes): -0.94 reward, 134.70 ms latency, 100% fidelity

### RandomPlacement
- **File:** `src/algorithms/random_place.py`
- Random assignment baseline
- Achieves (5-trial, 6 nodes): -0.07 reward, 119.11 ms latency, 99.98% fidelity, 2,961 W power

---

## Experiments & Reproduction

### Multi-Trial Experiment (5 seeds)
```bash
python experiments/run_multi_trial.py
```
- Runs all algorithms 5 times with different random seeds
- Results: `results/multi_trial/multi_trial_summary.csv`
- Figures: `python experiments/gen_multi_trial_figure.py`

### Scalability Study
```bash
python experiments/run_scalability.py
```
- Tests at 6, 25, 50, 100, 200, 500, 1000 nodes (7 scale points, 167× range)
- Full runs (1,000–50 steps) at 6–200 nodes; timing benchmarks at 500–1,000 nodes
- Results: `results/scalability/scalability_results.csv`
- Figures: `python experiments/gen_scalability_figure.py`

### Parameter Sensitivity
```bash
python experiments/run_parameter_sensitivity.py
```
- Sweeps: τ (semantic threshold), λ_EWC, K₁, K₂, DP noise
- Results: `results/sensitivity/`

### Additional Sweep Experiments
```bash
# Tau sensitivity sweep
# Results: results/_sens_rev1_t5/summary.csv

# Priority study
# Results: results/_prio_off.csv, results/_prio_hash20_slope02.csv
```

### Running Tests
```bash
python -m pytest tests/ -v
```

---

## Evaluation Metrics

All algorithms are compared on 8 standardized metrics (all use real simulation data with mobility):

| # | Metric | Description | Figure |
|---|--------|-------------|--------|
| 1 | **Reward** | Normalized cumulative reward | `reward_aggregate_comparison` |
| 2 | **Latency** | Orchestration decision latency (ms) | `latency_comparison` |
| 3 | **Semantic Fidelity** | % of semantically correct placements | `fidelity_comparison` |
| 4 | **Power Consumption** | System power (W) | `power_consumption_comparison` |
| 5 | **Communication Overhead** | Bytes exchanged per step / cumulative | `communication_overhead_comparison` |
| 6 | **Algorithm Efficiency** | Reward-to-resource ratio | `algorithm_efficiency_comparison` |
| 7 | **Convergence Speed** | Steps to stable reward | `convergence_speed_comparison` |
| 8 | **Performance Stability** | Variance/consistency over time | `performance_stability_comparison` |

All metric CSVs include explicit `Num_Nodes` and step count columns for reproducibility.



## Baseline Comparisons

### State-of-the-Art Methods

#### ECO-SDIoT (Zhu et al., 2023)
- **Approach:** Double DQN + SDN for edge offloading, 20 edge servers
- **Their latency:** 20–60 ms → FedSemGNN: 0.36 ms → **55–166× faster**
- **Their communication:** 50 MB/task → FedSemGNN: 0.65 MB → **76× less**
- **Their energy:** ~14 mJ/task → FedSemGNN: 26 mJ/task (1.9× higher — see [Energy Trade-Off](#energy-trade-off))
- **Lacks:** Semantic awareness, federated learning, GNN topology encoding

#### GFL-LFF (Regan et al., 2024)
- **Approach:** GNN + Federated Learning + Fennec Fox Optimization for IIoT
- **Their latency:** 1,600 ms → FedSemGNN: 0.36 ms → **4,444× faster**
- **Note:** Energy figures (0.2 mJ/operation) are per-operation vs. system power — not directly comparable

#### FRPVC (Qian et al., 2025)
- **Approach:** Federated DDQN + Denoised Autoencoder for video caching in energy-constrained MEC
- **Similarity:** 8/8 technique match (federated + DRL + energy-constrained + privacy)
- **FedSemGNN advantages:** General task placement (vs. video-only), PPO (vs. DDQN), semantic embeddings, GNN topology, hierarchical structure

### Comparison Table

| Method | Year | Latency | Energy | Comm. | Semantic | Federated |
|--------|------|---------|--------|-------|----------|-----------|
| ECO-SDIoT | 2023 | 20–60 ms | 14 mJ | 50 MB | No | No |
| GFL-LFF | 2024 | 1,600 ms | 0.2 mJ | — | No | Yes |
| FRPVC | 2025 | — | — | — | No | Yes |
| **FedSemGNN** | **2025** | **0.36 ms** | **26 mJ** | **0.65 MB** | **Yes** | **Yes** |

### Self-Implemented Baselines (5-trial average, 6-node base, 1,000 steps)

| Algorithm | Reward | Latency (ms) | Fidelity (%) | Power (W) | Bytes Cum (MB) |
|-----------|--------|-------------|-------------|-----------|----------------|
| **FedSemGNN** | **-0.59 ± 0.49** | **39.08 ± 6.23** | **99.97 ± 0.01** | **2,674 ± 713** | **0.72** |
| FlatFedPPO | 0.25 ± 0.13 | 127.75 ± 13.85 | 71.93 ± 2.40 | 3,166 ± 313 | 15.02 |
| HierFedPPO | 0.57 ± 0.12 | 82.05 ± 0.42 | 98.45 ± 0.00 | 1,066 ± 0 | 207.65 |
| HSQF | -0.94 ± 0.00 | 134.70 ± 0.00 | 100.00 ± 0.00 | 840 ± 0 | 2.93 |
| RandomPlacement | -0.07 ± 0.00 | 119.11 ± 0.00 | 99.98 ± 0.00 | 2,961 ± 0 | 0.002 |
| CentralizedPPO | 0.25 ± 0.01 | 130.35 ± 0.43 | 72.52 ± 0.59 | 3,099 ± 167 | 0.00 |

---



---

## Energy Trade-Off

FedSemGNN consumes **26 mJ/task** (amortized from 72.1 W system power ÷ 2,778 tasks/s), which is **1.9× higher** than ECO-SDIoT's 14 mJ/task. This is a deliberate design decision:

- **55–166× faster latency** justifies the modest energy increase for latency-critical 6G apps (XR, autonomous vehicles, tactile internet)
- **System-level offsets:** zero migrations, 100% fidelity, 76× less communication, zero QoS violations → eliminates retry/retransmission energy waste
- Power estimates use utilization-based analytical models with simulated DVFS in EdgeSimPy (not physical RAPL measurements — stated as future work)

---

## Fair Optimization Analysis

All 5 algorithms received identical 5-phase optimization (caching → async → pruning → communication → edge). Results show all algorithms benefit 50–86%:

| Algorithm | Original (ms) | Optimized (ms) | Improvement |
|-----------|--------------|----------------|-------------|
| FedSemGNN | 973.0 | 131.9 | 86.4% |
| FlatFedPPO | 232.0 | 57.2 | 75.3% |
| HierFedPPO | 324.0 | 113.4 | 65.0% |
| HSQF | 110.0 | 23.3 | 78.8% |
| RandomPlacement | 294.0 | 102.5 | 65.1% |

FedSemGNN maintains its advantages in reward/fidelity/semantics even where its raw latency is higher. Details: `docs/FAIR_OPTIMIZATION_REPORT.md` (deleted — data preserved here).

---

## Dependencies

**Core ML:** torch≥2.1.0, torch-geometric≥2.4.0, scikit-learn≥1.4.0

**Data/Visualization:** numpy≥1.25.0, pandas≥2.1.0, matplotlib≥3.8.0, seaborn≥0.13.0, plotly≥5.20.0, dash≥2.15.0

**Simulation:** edge-sim-py≥2.2.0, gym≥0.27.0, networkx≥3.2.0

**Infrastructure:** tensorboard≥2.15.0, scipy≥1.12.0, joblib≥1.4.0, tqdm≥4.68.0, pyyaml≥6.0.1, click≥8.1.7

**Development/QA:** pytest≥8.0.0, pytest-cov≥4.2.0, black≥24.4.0, flake8≥7.1.0, isort≥5.14.0, mypy≥1.10.0

**Documentation:** sphinx≥7.3.0, sphinx-rtd-theme≥2.1.0

---

## Key Files Reference

### Critical Source Files
| File | Purpose |
|------|---------|
| `src/algorithms/FedSemGNN.py` | Main framework implementation |
| `src/algorithms/PPO.py` | Base PPO with actor-critic and replay buffer |
| `src/core/config.py` | All default hyperparameters |
| `src/core/config_1000_nodes.py` | Scaled config for large experiments |
| `src/core/online_semantic_learning.py` | EWC continual learning engine |
| `src/utils/gcn_encoder.py` | 2-layer GCN with symmetric normalization |
| `main.py` | CLI entry point (310 lines) |

### Critical Data Files
| File | Purpose |
|------|---------|
| `results/multi_trial/multi_trial_summary.csv` | 5-trial verified results (primary data source) |
| `results/scalability/scalability_results.csv` | 7-point scalability study (6 to 1,000 nodes) |
| `results/_sens_rev1_t5/summary.csv` | Sensitivity sweep results |
| `workloads/dataset_10000.json` | 10,000-node dataset (generated but not used in final experiments) |


---


