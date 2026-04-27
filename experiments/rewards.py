# rewards.py

import matplotlib.pyplot as plt
from common_sources import SOURCES
from metrics_loader import load_metrics, aggregate_for_bars

names, vals = [], []
for name, path in SOURCES.items():
    df = load_metrics(path)
    agg = aggregate_for_bars(df)
    names.append(name); vals.append(agg["reward"])

fig, ax = plt.subplots(figsize=(9,5))
bars = ax.bar(names, vals)
ax.set_title("Reward ▲ Higher is Better"); ax.set_ylabel("Reward")
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v*1.01, f"{v:.1f}", ha="center", va="bottom")
fig.tight_layout()
fig.savefig("rewards.png", dpi=300)
fig.savefig("rewards.pdf")
print("✅ rewards.png / rewards.pdf")
