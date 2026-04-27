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
BASENAME = "timeline"

# --- Your DOT graph ---
DOT = r'''
digraph FedSemGNN_Timeline_Sectioned {
  layout=dot;
  rankdir=TB;
  fontname="Helvetica";
  fontsize=10;

  node [shape=box, style=filled, width=1.3, height=0.6, fontname="Helvetica", fontsize=9];

  // Row 1 (t=0–2): Setup
  t0 [label="t = 0", fillcolor=lightgray];
  t1 [label="t = 1", fillcolor=lightgray];
  t2 [label="t = 2", fillcolor=lightgray];

  // Row 2 (t=3–5): First sync cycle
  t3 [label="t = 3\n🔁 Intra Sync", fillcolor=deepskyblue];
  t4 [label="t = 4", fillcolor=lightgray];
  t5 [label="t = 5", fillcolor=lightgray];

  // Row 3 (t=6–8): Second sync cycle
  t6 [label="t = 6\n🔁 Intra Sync", fillcolor=mediumseagreen];
  t7 [label="t = 7", fillcolor=lightgray];
  t8 [label="t = 8", fillcolor=lightgray];

  // Row 4 (t=9–10): Intra + Inter sync
  t9 [label="t = 9\n🔁 Intra + Inter Sync", fillcolor=salmon];
  t10 [label="t = 10", fillcolor=lightgray];
  filler [label="", style=invis, width=0];

  // Rank constraints for rows
  { rank = same; t0; t1; t2; }
  { rank = same; t3; t4; t5; }
  { rank = same; t6; t7; t8; }
  { rank = same; t9; t10; filler; }

  // Timeline arrows
  t0 -> t1 -> t2 -> t3 -> t4 -> t5 -> t6 -> t7 -> t8 -> t9 -> t10;

  // Legend
  Legend [shape=note, fontsize=9, fontcolor=black, fillcolor=beige,
    label="🔁 Intra = Cluster Sync (K₁)\n🔁 Intra + Inter = Federated Sync (K₂)\nSync steps are color-highlighted"];

  { rank = same; t10 -> Legend [style=invis]; }
}
'''

# --- Render both PDF and PNG ---
src = Source(DOT, filename=str(OUT_DIR / BASENAME), engine="dot")

pdf_path = src.render(format="pdf", cleanup=True)
png_path = src.render(format="png", cleanup=True)

print(f"PDF saved to: {pdf_path}")
print(f"PNG saved to: {png_path}")
