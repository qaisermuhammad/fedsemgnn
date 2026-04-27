# Major Revision — Response Matrix (Feb 20, 2026)

This document maps each editor/reviewer point to concrete paper/code changes in this repository.

## Reviewer #1

### 1) Abstract too lengthy
- Addressed by condensing the abstract to focus on: (i) problem, (ii) method, (iii) knobs ($\tau$, $\lambda_{\mathrm{EWC}}$), (iv) baselines, (v) headline outcomes.
- Paper edits: sections/main.tex (Abstract); sections/abstract.tex kept consistent.

### 2) Semantic similarity threshold $\tau=0.3$ lacks justification + adaptation to different services
- Added explicit definition of semantic acceptance threshold and clarified it as a tunable knob (default, not arbitrary fixed).
- Added priority-adaptive thresholding: $\tau_i = \mathrm{clip}(\tau_0 + \kappa (p_i-0.5),\,\cdot)$ to adapt semantic strictness for URLLC/emergency services.
- Added effective-threshold instrumentation in code (`Semantic_tau_effective_{min,mean,max}`) so experiments can report what was actually applied.
- Paper edits: sections/main.tex (Proposed Methodology → Semantic Embedding → threshold adaptation).
- Code/experiments: src/algorithms/FedSemGNN.py (metrics columns; priority-adaptive tau); experiments/run_parameter_sensitivity.py (tau sweeps).
- Evidence: results/_sens_rev1_t5/summary.csv (tau sweep rows; 5 trials); summarized in paper Table \ref{tab:param_sensitivity}.

### 3) EWC parameter $\lambda_{\mathrm{EWC}}=0.4$ lacks selection logic + no sensitivity
- Clarified the stability–plasticity tradeoff controlled by $\lambda_{\mathrm{EWC}}$ and stated it is exposed as a tunable knob.
- Sensitivity support: config overrides propagate into the semantic encoder via env var (`FEDSEMGNN_EWC_LAMBDA`) and the sweep script supports it.
- Paper edits: sections/main.tex (Semantic Embedding → Continual learning regularization subsection).
- Code/experiments: src/core/online_semantic_learning.py (env override); experiments/run_parameter_sensitivity.py (lambda sweeps).
- Evidence: results/_sens_rev1_t5/summary.csv (EWC sweep rows; 5 trials); summarized in paper Table \ref{tab:param_sensitivity}.

### 4) No task priority differentiation (emergency vs ordinary)
- Implemented priority-aware scheduling diagnostics and reward shaping via priority-weighted latency.
- Added injected priority mode for controlled experiments (`FEDSEMGNN_PRIORITY_MODE=hash20`).
- Added quantitative emergency-vs-ordinary metrics in the output CSV:
  - `SvcLatency_emergency_mean_ms`, `SvcLatency_ordinary_mean_ms`
  - `Fidelity_emergency_pct`, `Fidelity_ordinary_pct`
  - along with `SvcLatency_weighted_ms`.
- Paper edits: sections/main.tex (Reward Function updated to weighted latency; Evaluation adds Priority-Aware Scheduling Study + Table).
- Code: src/algorithms/FedSemGNN.py (priority injection persistence + stratified metrics).

### 5) More related works on 6G edge
- Expanded related-work discussion with 6G/MEC context and cross-layer intelligent optimization.
- Added a reviewer-suggested reference (ANNS) with a verified DOI entry.
- Paper edits: sections/main.tex (Related Work additions).
- Bibliography edits: sections/new_references.bib (added chen2025anns; mao2017mec_survey).

### 6) Baselines incomplete; missing centralized RL (SAC/TD3) and MARL
- Added a runnable centralized RL baseline: `CentralizedPPO` (single agent, zero federated comm) to provide an apples-to-apples centralized control baseline.
- Added related-work context for SAC/TD3 and MARL (MAPPO) and explained the combinatorial action-space challenge for placement.
- Paper edits: sections/main.tex (Baseline Algorithms updated; Related Work adds SAC/TD3/MAPPO context).
- Code: src/algorithms/centralized_ppo.py + centralized-mode path in src/algorithms/flat_fedppo.py.
- Bibliography edits: sections/new_references.bib (haarnoja2018sac; fujimoto2018td3; yu2021mappo).

### 7) Engineering compatibility / deployment details missing
- Added a deployment/compatibility subsection describing FedSemGNN as a control-plane decision module with clear telemetry-in / placement-out integration points.
- Paper edits: sections/main.tex (System Architecture → Compatibility with Existing 6G Edge Platforms).

## Reviewer #2 — novelty/generalization/scalability doubts

- Clarified that key parameters are defaults, not fixed design constants, and are exposed as experiment knobs.
- Added sensitivity/priority instrumentation so claims are backed by executable measurements rather than narrative.
- Strengthened positioning: FedSemGNN’s contribution is the *combined* privacy-preserving hierarchical FRL + topology encoding + semantic continual learning in a real-time control-plane loop, with explicit scaling validation up to 10,000 nodes.
- Paper edits: sections/main.tex (Abstract; Contributions; Methodology; Evaluation additions).

## Where to find the evidence

- Paper source: sections/main.tex
- Bibliography: sections/new_references.bib
- Priority and threshold instrumentation: src/algorithms/FedSemGNN.py
- Sensitivity runner: experiments/run_parameter_sensitivity.py
- Sensitivity outputs: results/_sens_rev1_t5/summary.csv and results/_sens_rev1_t5/summary_trials.csv (used in Table \ref{tab:param_sensitivity})
- Centralized baseline: src/algorithms/centralized_ppo.py (invokes centralized mode in flat_fedppo)

## Quantitative priority-study numbers (generated from repo runs)

Computed from two 50-step runs on Feb 20, 2026:
- Baseline (no priority injection): `results/_prio_off.csv`
- Priority-aware (hash20 + slope=0.2): `results/_prio_hash20_slope02.csv`

These numbers are summarized in the paper’s Table \ref{tab:priority_study}.
