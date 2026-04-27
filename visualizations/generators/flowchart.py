from graphviz import Source
from pathlib import Path
import os, shutil

# --- Optional: ensure Graphviz path on Windows ---
GV_BIN = r"C:\Program Files\Graphviz\bin"
if not shutil.which("dot") and Path(GV_BIN).exists():
    os.environ["PATH"] = GV_BIN + os.pathsep + os.environ.get("PATH", "")
    os.environ["GRAPHVIZ_DOT"] = str(Path(GV_BIN) / "dot.exe")

# --- Output config ---
OUT_DIR = Path("diagramsdotandpython")
OUT_DIR.mkdir(exist_ok=True)
BASENAME = "flowchart"

# --- Your DOT graph ---
DOT = r'''
digraph FedSemGNN_Flowchart {
  rankdir=TB;
  fontsize=11;
  node [fontname=Helvetica, style=filled, fontsize=10];

  // Nodes with modular coloring
  ServiceArrive  [label="Service Arrival", shape=box, fillcolor=lightyellow];
  ExtractEmbed   [label="Extract & Project\nSemantic Embedding", shape=box, fillcolor=lightgoldenrod1];
  GCNEncode      [label="GCN Encoding\n(Local + Neighbor Features)", shape=box, fillcolor=lightblue];
  MatchCluster   [label="Select Cluster (k*)", shape=box, fillcolor=lavender];
  MatchServer    [label="Select Server (i*)", shape=box, fillcolor=lavender];
  Deploy         [label="Deploy Service", shape=box, fillcolor=lightgreen];
  ComputeReward  [label="Compute Reward", shape=box, fillcolor=khaki];
  PPOUpdate      [label="Local PPO Update", shape=box, fillcolor=plum];
  SyncCheck      [label="Sync Trigger?\n(step % K == 0)", shape=diamond, fillcolor=salmon];
  SyncStep       [label="Federated Sync\n(Global DP Aggregation)", shape=box, fillcolor=tomato];
  NextStep       [label="Next Step", shape=box, fillcolor=gray95];

  // Flow connections
  ServiceArrive  -> ExtractEmbed;
  ExtractEmbed   -> GCNEncode;
  GCNEncode      -> MatchCluster;
  MatchCluster   -> MatchServer;
  MatchServer    -> Deploy;
  Deploy         -> ComputeReward;
  ComputeReward  -> PPOUpdate;
  PPOUpdate      -> SyncCheck;

  // Conditional branches
  SyncCheck -> SyncStep [label="Yes", color=black];
  SyncStep  -> NextStep;
  SyncCheck -> NextStep [label="No", style=dashed, color=gray];
}
'''

# --- Render both PDF and PNG ---
src = Source(DOT, filename=str(OUT_DIR / BASENAME), engine="dot")

pdf_path = src.render(format="pdf", cleanup=True)
png_path = src.render(format="png", cleanup=True)

print(f"PDF saved to: {pdf_path}")
print(f"PNG saved to: {png_path}")
