# common_sources.py
from pathlib import Path
import re

RESULTS_DIR = Path("results")

# Strategy keys you want to show (names as they should appear in plots/tables)
TARGETS = ["FedSemGNN", "FlatFedPPO", "HierFedPPO", "HSQF Heur.", "Random"]

# How we detect a strategy from a folder name
ALIAS_MAP = {
    r"^FedSemGNN": "FedSemGNN",
    r"^FlatFedPPO": "FlatFedPPO",
    r"^HierFedPPO": "HierFedPPO",
    r"^HSQF": "HSQF Heur.",
    r"^RandomPlacement|^Random$": "Random",
}

def normalize_strategy(folder_name: str) -> str | None:
    for pat, label in ALIAS_MAP.items():
        if re.search(pat, folder_name, re.IGNORECASE):
            return label
    return None

def score_folder(p: Path) -> tuple[int, int, int]:
    """
    Higher is better.
    Prefer 1000steps > 500steps, prefer 'gcn' over 'linear', then newer mtime.
    """
    name = p.name.lower()
    steps = 1000 if "1000" in name else (500 if "500" in name else 0)
    enc   = 1 if "gcn" in name else 0
    mtime = int(p.stat().st_mtime)
    return (steps, enc, mtime)

def discover_sources():
    sources = {}
    for run_dir in RESULTS_DIR.iterdir():
        if not run_dir.is_dir():
            continue
        csv = run_dir / "fedsemgnn_metrics.csv"
        if not csv.exists():
            continue
        label = normalize_strategy(run_dir.name)
        if not label:
            continue
        # keep the best-scoring folder for this label
        if label not in sources:
            sources[label] = csv
        else:
            current = sources[label]
            # compare scores of folders that contain the csv
            best_dir = sources[label].parent
            if score_folder(run_dir) > score_folder(best_dir):
                sources[label] = csv

    # keep only targets in desired order if present
    ordered = {k: sources[k] for k in TARGETS if k in sources}
    return ordered

# Public: SOURCES dict used by plotting scripts
SOURCES = discover_sources()
if not SOURCES:
    raise SystemExit("No fedsemgnn_metrics.csv files found under results/.")
