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
BASENAME = "DataPipeline"

# --- Your DOT graph ---
DOT = r'''
digraph FedSemGNN_DataPipeline_Refined { 
  rankdir=LR;
  fontsize=10;
  fontname="Helvetica";

  node [shape=box, style=filled, fillcolor=khaki, fontname=Helvetica, fontsize=10];

  // Nodes
  RawCSV     [label="Raw Metrics\n(CSV logs)", shape=folder, fillcolor=lightyellow];
  Stitch     [label="stitch_baseline_csvs.py\n⟶ Merge across strategies"];
  Summarize  [label="summarize_results.py\n⟶ Compute aggregate metrics"];
  TableGen   [label="comparative_table.py\n⟶ Format comparison tables"];
  PlotGen    [label="plot_*.py\n⟶ Generate performance figures"];
  Output     [label="Final Outputs:\nTables + Figures", shape=note, fillcolor=palegreen];

  // Arrows
  RawCSV -> Stitch;
  Stitch -> Summarize;
  Summarize -> TableGen;
  TableGen -> PlotGen;
  PlotGen -> Output;

  // Optional Legend
  Legend [shape=note, label="🔁 Reproducible Analysis Pipeline", fontsize=9, style=filled, fillcolor=white];
}
'''

# --- Render both PDF and PNG ---
src = Source(DOT, filename=str(OUT_DIR / BASENAME), engine="dot")

pdf_path = src.render(format="pdf", cleanup=True)
png_path = src.render(format="png", cleanup=True)

print(f"PDF saved to: {pdf_path}")
print(f"PNG saved to: {png_path}")
