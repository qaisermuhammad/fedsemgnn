from graphviz import Source
from pathlib import Path
import os, shutil

# --- Make sure NEATO is used (no dot -Kneato) ---
# You may need to adjust this path to your Graphviz installation directory
GV_BIN = r"C:\Program Files\Graphviz\bin"
if Path(GV_BIN).exists():
    os.environ["PATH"] = GV_BIN + os.pathsep + os.environ.get("PATH", "")
os.environ.pop("GRAPHVIZ_DOT", None)  # avoid forcing dot.exe

# --- Output config ---
OUT_DIR = Path("diagramsdotandpython")
OUT_DIR.mkdir(exist_ok=True)
BASENAME = "flowchart_LR"

# --- Coordinates: strictly left→right on y=0 row ---
ROW_Y = 0.0
Y_UP  = 1.10
Y_DN  = -1.10
# Compact, readable x-spacing
X = {i: round(i * 1.3, 3) for i in range(0, 13)}  # 0..12 (Increased spacing slightly for clarity)

DOT = fr'''
digraph FedSemGNN_Flowchart {{
  // Use NEATO with pinned positions to guarantee LEFT→RIGHT (no vertical ranks)
  graph [
    overlap=false,
    splines=ortho,  // Use ortho for straight lines, though we manually control bends
    pad="0.04",
    margin="0.04",
    bgcolor="white",
    fontname="Helvetica",
    fontsize=11
  ];
  node [
    shape=box,
    style="rounded,filled",
    fontname="Helvetica",
    fontsize=9,
    color="#D0D7DE",
    fillcolor="white",
    penwidth=1.0,
    width=1.7,
    height=0.5,
    margin="0.04,0.04"
  ];
  edge [
    color="#374151",
    arrowsize=0.65,
    penwidth=1.05,
    fontname="Helvetica",
    fontsize=8.5,
    labeldistance=1.0
  ];

  // -------- Main row nodes (ALL pinned on y=0) --------
  ServiceArrive [label="Service Arrival",                         pos="{X[0]},{ROW_Y}!",  pin=true, fillcolor="lightgoldenrod1"];
  ExtractEmbed  [label="Extract & Project\nSemantic Embedding", pos="{X[1]},{ROW_Y}!",  pin=true, fillcolor="lightgoldenrod1"];
  GCNEncode     [label="GCN Encoding\n(Local+Neighbor)",         pos="{X[2]},{ROW_Y}!",  pin=true, fillcolor="lightblue"];
  MatchCluster  [label="Select Cluster (k*)",                     pos="{X[3]},{ROW_Y}!",  pin=true, fillcolor="lavender"];
  MatchServer   [label="Select Server (i*)",                      pos="{X[4]},{ROW_Y}!",  pin=true, fillcolor="lavender"];
  Deploy        [label="Deploy Service",                          pos="{X[5]},{ROW_Y}!",  pin=true, fillcolor="honeydew"];
  ComputeReward [label="Compute Reward",                          pos="{X[6]},{ROW_Y}!",  pin=true, fillcolor="khaki"];
  PPOUpdate     [label="Local PPO Update",                        pos="{X[7]},{ROW_Y}!",  pin=true, fillcolor="plum"];
  SyncCheck     [label="Sync Trigger?\n(step % K == 0)", shape=diamond, height=0.8, width=1.8,
                                                           pos="{X[8]},{ROW_Y}!",  pin=true, fillcolor="salmon"];

  // -------- Upper branch & advance (pinned) --------
  SyncStep      [label="Federated Sync\n(Global DP Aggregation)", pos="{X[10]},{Y_UP}!", pin=true, fillcolor="tomato"];
  Advance       [label="Advance t := t+1", shape=ellipse,        pos="{X[11]},{ROW_Y}!", pin=true, fillcolor="gray95", width=1.45, height=0.42];

  // -------- Invisible bend points (pinned) to create right-angle looks --------
  // *** NEW *** YES path bends: up, then right
  Y1_up  [label="", shape=point, width=0.01, height=0.01, style=invis, pos="{X[8]},{Y_UP}!",  pin=true];

  // Bend from SyncStep down to Advance
  Y2_bend [label="", shape=point, width=0.01, height=0.01, style=invis, pos="{X[11]},{Y_UP}!", pin=true];

  // *** NEW *** NO path bends: down, then left, then up
  N1_down [label="", shape=point, width=0.01, height=0.01, style=invis, pos="{X[8]},{Y_DN}!", pin=true];
  N2_left [label="", shape=point, width=0.01, height=0.01, style=invis, pos="{X[0]},{Y_DN}!", pin=true];

  // Advance loop bends: down then left to ServiceArrival
  L1V  [label="", shape=point, width=0.01, height=0.01, style=invis, pos="{X[11]+0.4},{Y_DN}!", pin=true];
  L1H  [label="", shape=point, width=0.01, height=0.01, style=invis, pos="{X[0]-0.5},{Y_DN}!", pin=true];

  // -------- Main pipeline (strict left→right; ports keep edges clean) --------
  ServiceArrive:e -> ExtractEmbed:w;
  ExtractEmbed:e  -> GCNEncode:w;
  GCNEncode:e     -> MatchCluster:w;
  MatchCluster:e  -> MatchServer:w;
  MatchServer:e   -> Deploy:w;
  Deploy:e        -> ComputeReward:w;
  ComputeReward:e -> PPOUpdate:w;
  PPOUpdate:e     -> SyncCheck:w;

  // -------- YES path (orthogonal via bend points) --------
  // Connect to the North port, go up, then turn right
  SyncCheck:n -> Y1_up        [label=" Yes", fontcolor="#0F766E", color="#0F766E"];
  Y1_up       -> SyncStep:w   [color="#0F766E"];

  // Right-angled connection from SyncStep to Advance
  SyncStep:e  -> Y2_bend      [color="#0F766E"];
  Y2_bend     -> Advance:n    [color="#0F766E"];

  // -------- NO path (clean rectangular loopback) --------
  // Connect to the South port, go down, turn left, then connect back
  SyncCheck:s   -> N1_down         [label="No ", style=dashed, color="#9CA3AF", fontcolor="#9CA3AF"];
  N1_down       -> N2_left         [style=dashed, color="#9CA3AF"];
  N2_left       -> ServiceArrive:s [style=dashed, color="#9CA3AF"];

  // -------- Advance loop (orthogonal-like dashed path) --------
  Advance:e   -> L1V             [style=dashed, color="#6B7280"];
  L1V         -> L1H             [style=dashed, color="#6B7280"];
  L1H         -> ServiceArrive:w [style=dashed, color="#6B7280"];
}}
'''

# Render with NEATO (pinned positions)
src = Source(DOT, filename=str(OUT_DIR / BASENAME), engine="neato")
try:
    pdf_path = src.render(format="pdf", cleanup=True)
    png_path = src.render(format="png", cleanup=True)
    print(f"Successfully generated diagrams.")
    print(f"PDF saved to: {pdf_path}")
    print(f"PNG saved to: {png_path}")
except Exception as e:
    print(f"An error occurred during rendering: {e}")
    print("Please ensure Graphviz is installed and the path in the script is correct.")

