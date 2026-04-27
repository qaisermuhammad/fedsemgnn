import pandas as pd

def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """
    Render a DataFrame as a GitHub-flavored Markdown table without external libs.
    """
    cols = list(df.columns)
    md = "| " + " | ".join(cols) + " |\n"
    md += "| " + " | ".join("---" for _ in cols) + " |\n"
    for row in df.itertuples(index=False, name=None):
        md += "| " + " | ".join(str(x) for x in row) + " |\n"
    return md

def final_row(df, name, hier, sem, rl):
    last = df.iloc[-1]
    return {
        "Strategy":     name,
        "Hierarchical": "✅" if hier else "❌",
        "Semantic":     "✅" if sem else "❌",
        "RL-Based":     "✅" if rl  else "❌",
        "Reward":       round(last["Reward"], 1),
        "Latency":      f"{last['Latency']:.2f}s" if pd.notna(last["Latency"]) else "N/A",
        "Power":        f"{last['Power']:.1f}W",
        "Fidelity":     f"{last['Fidelity']*100:.1f}%" if pd.notna(last["Fidelity"]) else "N/A",
        "Bytes Exch.":  f"{last['BytesExchanged']/1e6:.1f}MB"
    }

baselines = [
    ("results/flat_fedppo_metrics.csv",  "FlatFedPPO",       False, False, True),
    ("results/hier_fedppo_metrics.csv",  "HierFedPPO",       True,  False, True),
    ("results/hsqf_metrics.csv",         "HSQF Heur.",       False, True,  False),
    ("results/random_place_metrics.csv", "Random Placement", False, False, False),
    ("results/fedsemgnn_metrics.csv",    "FedSemGNN (Ours)", True,  True,  True),
]

rows = []
for path, name, h, s, r in baselines:
    df = pd.read_csv(path)
    rows.append(final_row(df, name, h, s, r))

table = pd.DataFrame(rows)
print(dataframe_to_markdown(table))
