from pathlib import Path
from graphviz import Source
import os, re, shutil

# --- Minimal env fix: only patch PATH if needed ---
GV_BIN = r"C:\Program Files\Graphviz\bin"
if not shutil.which("dot"):
    os.environ["PATH"] = GV_BIN + os.pathsep + os.environ.get("PATH", "")
    os.environ["GRAPHVIZ_DOT"] = os.path.join(GV_BIN, "dot.exe")

# --- Layout knobs (edit as you like) ---
CFG = dict(
    OUT_DIR="diagramsdotandpython",
    NAME="architecture",
    ORIENTATION="LR",          # "TB" or "LR"
    NODESEP="0.2",
    RANKSEP="0.4",
    SPLINES="spline",          # "spline" | "ortho" | "line"
    DPI="500",
    FORMATS=("pdf", "png"),
)

DOT = r'''
digraph FedSemGNN_FullArch {
  rankdir=LR;
  fontsize=11;
  compound=true;
  node [fontname="Helvetica", style=filled, fontsize=10];

  // User Input
  UserDevice [label="User Devices\n(XR/AR)", shape=ellipse, fillcolor=gold];
  SemanticEncoder [label="Semantic Encoder", shape=box, fillcolor=lightgoldenrod1];
  SemanticVec [label="Semantic Embedding", shape=plaintext];

  // CLUSTER 1
  subgraph cluster_Cluster1 {
    label="Cluster 1";
    style=dashed;
    color=blue;

    ResourceMonitor1 [label="Resource Monitor", shape=component, fillcolor=lightcyan];
    NodeA [label="Edge Node A", shape=box, fillcolor=lightblue];
    NodeB [label="Edge Node B", shape=box, fillcolor=lightblue];
    GCN1 [label="GCN Encoder", shape=parallelogram, fillcolor=skyblue];
    PPO1 [label="Local PPO Agent", shape=hexagon, fillcolor=plum];
    SyncBlock1 [label="Intra-cluster Sync\n$K_{intra}$", shape=note, fillcolor=lavender];
  }

  // CLUSTER 2
  subgraph cluster_Cluster2 {
    label="Cluster 2";
    style=dashed;
    color=darkgreen;

    ResourceMonitor2 [label="Resource Monitor", shape=component, fillcolor=mintcream];
    NodeC [label="Edge Node C", shape=box, fillcolor=lightgreen];
    NodeD [label="Edge Node D", shape=box, fillcolor=lightgreen];
    GCN2 [label="GCN Encoder", shape=parallelogram, fillcolor=palegreen];
    PPO2 [label="Local PPO Agent", shape=hexagon, fillcolor=thistle];
    SyncBlock2 [label="Intra-cluster Sync\n$K_{intra}$", shape=note, fillcolor=honeydew];
  }

  // Federated Aggregation
  FedAgg [label="Federated Aggregator", shape=box, fillcolor=salmon];
  DPNoise [label="DP Noise\nInjection", shape=ellipse, fillcolor=pink];
  GlobalPolicy [label="Global Policy\nDistribution", shape=parallelogram, fillcolor=mistyrose];

  // Inputs and Embedding
  UserDevice -> SemanticEncoder -> SemanticVec [arrowhead=none];
  SemanticVec -> NodeA; SemanticVec -> NodeB; SemanticVec -> NodeC; SemanticVec -> NodeD;

  // Resource State Flow
  ResourceMonitor1 -> NodeA; ResourceMonitor1 -> NodeB;
  ResourceMonitor2 -> NodeC; ResourceMonitor2 -> NodeD;

  // Intra-cluster logic
  NodeA -> GCN1; NodeB -> GCN1; GCN1 -> PPO1; PPO1 -> SyncBlock1 [label="Δθ₁"]; SyncBlock1 -> FedAgg;
  NodeC -> GCN2; NodeD -> GCN2; GCN2 -> PPO2; PPO2 -> SyncBlock2 [label="Δθ₂"]; SyncBlock2 -> FedAgg;

  // Fed Sync
  FedAgg -> DPNoise [style=dashed, label="Noise Applied"];
  DPNoise -> GlobalPolicy [label="π Aggregated"];

  GlobalPolicy -> PPO1 [ltail=cluster_Cluster1];
  GlobalPolicy -> PPO2 [ltail=cluster_Cluster2];
}
'''

def inject_layout(dot: str, *, orient, nodesep, ranksep, splines, dpi) -> str:
    # force rankdir
    dot = re.sub(r'rankdir\s*=\s*\w+;', f'rankdir={orient};', dot)
    # inject graph attrs right after the first '{'
    return re.sub(
        r'(\{)',
        r'\1\n  graph [overlap=false, splines=%s, nodesep=%s, ranksep=%s];\n  outputorder=edgesfirst;\n  dpi=%s;\n  edge [penwidth=1.1];'
        % (splines, nodesep, ranksep, dpi),
        dot, count=1
    )

def render(dot: str, outdir: str, name: str, formats=("pdf",)):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    dot = inject_layout(dot, orient=CFG["ORIENTATION"], nodesep=CFG["NODESEP"],
                        ranksep=CFG["RANKSEP"], splines=CFG["SPLINES"], dpi=CFG["DPI"])
    paths = {}
    for fmt in formats:
        src = Source(dot, filename=str(Path(outdir) / name), format=fmt, engine="dot")
        paths[fmt] = src.render(cleanup=True)
    return paths

if __name__ == "__main__":
    out = render(DOT, CFG["OUT_DIR"], CFG["NAME"], CFG["FORMATS"])
    print("Saved:", *[f"{k}: {v}" for k, v in out.items()], sep="\n ")
