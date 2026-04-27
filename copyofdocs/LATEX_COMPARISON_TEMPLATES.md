# LaTeX Comparison Table Templates

Use these templates once you have collected paper data.

---

## Template 1: Basic Comparison Table (Compact)

```latex
\begin{table}[htbp]
\centering
\caption{Performance Comparison with State-of-the-Art Methods}
\label{tab:literature_comparison}
\small
\begin{tabular}{@{}lcccc@{}}
\toprule
\textbf{Method} & \textbf{Latency (ms)} & \textbf{Power (W)} & \textbf{Comm. (MB)} & \textbf{Source} \\
\midrule
FedSemGNN (Ours) & \textbf{0.36} & \textbf{72.1} & \textbf{0.65} & This work \\
[Paper1 Method] & [value] & [value] & [value] & \cite{paper1} \\
[Paper2 Method] & [value] & [value] & [value] & \cite{paper2} \\
[Paper3 Method] & [value] & [value] & [value] & \cite{paper3} \\
[Paper4 Method] & [value] & [value] & [value] & \cite{paper4} \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Note: Results from cited works are taken from their published evaluations. 
Direct comparison should consider differences in experimental setups (see text for details).
\end{tablenotes}
\end{table}
```

---

## Template 2: Extended Comparison Table (More Metrics)

```latex
\begin{table*}[htbp]
\centering
\caption{Comprehensive Comparison with Recent Computer Networks Publications}
\label{tab:extended_comparison}
\small
\begin{tabular}{@{}lccccccl@{}}
\toprule
\textbf{Method} & \textbf{Year} & \textbf{Latency} & \textbf{Power} & \textbf{Comm.} & \textbf{Reward} & \textbf{Approach} & \textbf{Ref.} \\
 & & \textbf{(ms)} & \textbf{(W)} & \textbf{(MB)} & & & \\
\midrule
\textbf{FedSemGNN} & 2025 & \textbf{0.36} & \textbf{72.1} & \textbf{0.65} & \textbf{0.91} & Fed-RL+GNN+Sem & This work \\
\midrule
\multicolumn{8}{l}{\textit{Federated Learning Approaches}} \\
[Method Name] & [Year] & [X] & [X] & [X] & [X] & Federated RL & \cite{key1} \\
[Method Name] & [Year] & [X] & [X] & [X] & [X] & Hierarchical FL & \cite{key2} \\
\midrule
\multicolumn{8}{l}{\textit{Graph Neural Network Approaches}} \\
[Method Name] & [Year] & [X] & [X] & [X] & [X] & GNN-based & \cite{key3} \\
[Method Name] & [Year] & [X] & [X] & [X] & [X] & Graph+RL & \cite{key4} \\
\midrule
\multicolumn{8}{l}{\textit{Semantic/Context-Aware Approaches}} \\
[Method Name] & [Year] & [X] & [X] & [X] & [X] & Semantic Heuristic & \cite{key5} \\
[Method Name] & [Year] & [X] & [X] & [X] & [X] & Context RL & \cite{key6} \\
\midrule
\multicolumn{8}{l}{\textit{Standard RL Baselines}} \\
[Method Name] & [Year] & [X] & [X] & [X] & [X] & Centralized DQN & \cite{key7} \\
[Method Name] & [Year] & [X] & [X] & [X] & [X] & A3C & \cite{key8} \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Abbreviations: Fed-RL = Federated Reinforcement Learning, GNN = Graph Neural Network, 
Sem = Semantic-aware
\item Results from literature are adapted from original publications under comparable 
experimental conditions. Differences in simulation parameters and network configurations 
may affect direct comparability (see Section~\ref{sec:discussion}).
\end{tablenotes}
\end{table*}
```

---

## Template 3: Improvement Percentage Table

```latex
\begin{table}[htbp]
\centering
\caption{Relative Performance Improvements of FedSemGNN}
\label{tab:improvements}
\begin{tabular}{@{}lcccc@{}}
\toprule
\textbf{Baseline Method} & \textbf{Latency} & \textbf{Power} & \textbf{Comm.} & \textbf{Source} \\
 & \textbf{Improv.} & \textbf{Improv.} & \textbf{Improv.} & \\
\midrule
FlatFedPPO & 315$\times$ & 36.2$\times$ & 161$\times$ & This work \\
HierFedPPO & 222$\times$ & 14.7$\times$ & 50$\times$ & This work \\
HSQF & 127$\times$ & 7.4$\times$ & 25$\times$ & This work \\
\midrule
[Paper1 Method] & [X]\% & [X]\% & [X]\% & \cite{paper1} \\
[Paper2 Method] & [X]\% & [X]\% & [X]\% & \cite{paper2} \\
[Paper3 Method] & [X]\% & [X]\% & [X]\% & \cite{paper3} \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Improvements calculated as: (Baseline - FedSemGNN) / Baseline × 100\%
\item Literature baselines calculated from reported values with caveats noted in text.
\end{tablenotes}
\end{table}
```

---

## Template 4: Feature Comparison Matrix

```latex
\begin{table}[htbp]
\centering
\caption{Feature Comparison of Edge Orchestration Approaches}
\label{tab:feature_comparison}
\small
\begin{tabular}{@{}lcccccc@{}}
\toprule
\textbf{Method} & \textbf{Fed.} & \textbf{Hier.} & \textbf{GNN} & \textbf{Sem.} & \textbf{RL} & \textbf{Ref.} \\
\midrule
\textbf{FedSemGNN} & \checkmark & \checkmark & \checkmark & \checkmark & \checkmark & This work \\
\midrule
[Method 1] & \checkmark & \ding{55} & \ding{55} & \ding{55} & \checkmark & \cite{key1} \\
[Method 2] & \checkmark & \checkmark & \ding{55} & \ding{55} & \checkmark & \cite{key2} \\
[Method 3] & \ding{55} & \ding{55} & \checkmark & \ding{55} & \checkmark & \cite{key3} \\
[Method 4] & \ding{55} & \ding{55} & \ding{55} & \checkmark & \ding{55} & \cite{key4} \\
[Method 5] & \ding{55} & \ding{55} & \checkmark & \checkmark & \ding{55} & \cite{key5} \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Abbreviations: Fed. = Federated Learning, Hier. = Hierarchical, 
GNN = Graph Neural Network, Sem. = Semantic-aware, RL = Reinforcement Learning
\item \checkmark indicates feature is present; \ding{55} indicates feature is absent
\end{tablenotes}
\end{table}
```

---

## Template 5: Experimental Setup Comparison

```latex
\begin{table}[htbp]
\centering
\caption{Comparison of Experimental Configurations}
\label{tab:setup_comparison}
\small
\begin{tabular}{@{}lcccl@{}}
\toprule
\textbf{Method} & \textbf{Nodes} & \textbf{Duration} & \textbf{Simulator} & \textbf{Ref.} \\
 & & \textbf{(steps)} & & \\
\midrule
FedSemGNN & Heterogeneous & 1,000 & EdgeSimPy & This work \\
 & (4-16 cores) & & & \\
\midrule
[Method 1] & [X] & [X] & [Platform] & \cite{key1} \\
[Method 2] & [X] & [X] & [Platform] & \cite{key2} \\
[Method 3] & [X] & [X] & [Platform] & \cite{key3} \\
\bottomrule
\end{tabular}
\end{table}
```

---

## Text Template for Comparison Discussion

```latex
\subsection{Comparison with State-of-the-Art Methods}

To position FedSemGNN within the broader landscape of edge orchestration research, 
we compare our results with recent methods published in Computer Networks journal.

\textbf{Comparison with Federated Learning Approaches.}
[Author et al.]~\cite{paper1} proposed [Method Name], a federated reinforcement learning 
framework for edge computing. Their approach achieves [X] ms average latency and [X] W 
power consumption on a network of [X] edge nodes. While their method demonstrates 
[strength], it lacks [weakness that FedSemGNN addresses]. FedSemGNN achieves [X]\% 
lower latency and [X]\% better energy efficiency through [your key innovation].

\textbf{Comparison with GNN-Based Methods.}
[Author et al.]~\cite{paper2} introduced [Method Name], utilizing graph neural networks 
for topology-aware service placement. They report [metric values] on [experimental setup]. 
However, their approach does not incorporate [semantic awareness / federated learning / etc.]. 
FedSemGNN's integration of GNN with semantic embeddings enables [advantage], resulting 
in [X]\% improvement in [metric].

\textbf{Comparison with Semantic-Aware Methods.}
Recent work by [Author et al.]~\cite{paper3} explores semantic similarity for task 
placement, achieving [results]. While effective, their heuristic-based approach cannot 
adapt to dynamic conditions. FedSemGNN's reinforcement learning foundation enables 
continuous policy optimization, improving [metric] by [X]\%.

Table~\ref{tab:literature_comparison} summarizes the quantitative comparison. It is 
important to note that direct comparison should consider differences in experimental 
configurations, including network scale, workload characteristics, and simulation 
platforms. Despite these variations, FedSemGNN consistently demonstrates superior 
performance across key metrics, validating the benefits of combining semantic awareness, 
GNN topology encoding, and hierarchical federated learning.
```

---

## LaTeX Packages Needed

Add to your preamble:

```latex
\usepackage{booktabs}  % For professional tables
\usepackage{threeparttable}  % For table notes
\usepackage{pifont}  % For checkmarks and X marks
\usepackage{multirow}  % For multi-row cells
```

For checkmarks and X:
```latex
% Checkmark
\checkmark

% X mark
\ding{55}
```

---

## How to Use These Templates

1. **Choose appropriate template** based on what data you collect
2. **Fill in [placeholders]** with actual values from papers
3. **Replace citation keys** with your BibTeX keys
4. **Adjust column widths** if needed
5. **Add table notes** explaining differences
6. **Reference in text** with proper discussion

---

## Example Filled Template

```latex
\begin{table}[htbp]
\centering
\caption{Performance Comparison with State-of-the-Art Methods}
\label{tab:literature_comparison}
\small
\begin{tabular}{@{}lcccc@{}}
\toprule
\textbf{Method} & \textbf{Latency (ms)} & \textbf{Power (W)} & \textbf{Comm. (MB)} & \textbf{Source} \\
\midrule
FedSemGNN (Ours) & \textbf{0.36} & \textbf{72.1} & \textbf{0.65} & This work \\
FedEdge & 42.5 & 856.3 & 98.4 & \cite{Chen2024FedEdge} \\
GraphPlace & 35.2 & 943.7 & 45.8 & \cite{Zhang2023GraphPlace} \\
SemanticSched & 51.8 & 634.2 & -- & \cite{Kumar2024Semantic} \\
DeepOffload & 38.9 & 1205.5 & 125.3 & \cite{Wang2023DeepOffload} \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Note: Results from cited works are taken from their published evaluations. 
FedEdge and GraphPlace use similar EdgeSimPy-based setup; SemanticSched uses 
custom simulator; DeepOffload uses iFogSim. Communication overhead not reported 
in \cite{Kumar2024Semantic}.
\end{tablenotes}
\end{table}
```

---

## Next Steps

1. ✅ Collect paper data using PAPER_DATA_COLLECTION.md
2. ✅ Choose appropriate template
3. ✅ Fill in values
4. ✅ Add to your LaTeX paper
5. ✅ Write discussion text
6. ✅ I'll help review and refine!

Share your collected data and I'll help format it perfectly!
