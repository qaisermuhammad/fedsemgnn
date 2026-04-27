import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.table import Table
import warnings

# Suppress future warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# 🌟 Replace tick/cross emojis with Unicode symbols
def styled(val):
    if val == "✅": return "✔"
    if val == "❌": return "✖"
    return val

# 📊 Table data
data = {
    "Strategy": ["FlatFedPPO", "HierFedPPO", "HSQF Heur.", "Random Placement", "FedSemGNN (Ours)"],
    "Hierarchical": ["❌", "✅", "❌", "❌", "✅"],
    "Semantic":     ["❌", "❌", "✅", "❌", "✅"],
    "RL-Based":     ["✅", "✅", "❌", "❌", "✅"],
    "Reward":       [2314.7, 5785.0, 6754.3, 6945.6, 7896.0],
    "Latency":      ["6.00s", "0.33s", "0.28s", "0.27s", "0.31s"],
    "Power":        ["7685.2W", "4211.6W", "3242.8W", "3051.7W", "2101.0W"],
    "Fidelity":     ["N/A", "N/A", "100.0%", "N/A", "50.0%"],
    "Bytes Exch.":  ["25.5MB", "6.2MB", "0.2MB", "0.0MB", "2.9MB"]
}

df = pd.DataFrame(data)
df = df.applymap(styled)

# 💾 Save to CSV
df.to_csv("graphs/strategy_metrics.csv", index=False)
print("✅ CSV file saved as strategy_metrics.csv in the graphs directory")

# 🎨 PNG Table Visualization
fig, ax = plt.subplots(figsize=(12, 3.5))
ax.set_axis_off()

table = Table(ax, bbox=[0, 0, 1, 1])
n_rows, n_cols = df.shape
col_widths = [0.2, 0.1, 0.1, 0.1, 0.12, 0.12, 0.12, 0.12, 0.12]
cell_height = 0.15

# 🔠 Header Row
for i, label in enumerate(df.columns):
    cell = table.add_cell(0, i, col_widths[i], cell_height, text=label, loc='center', facecolor='#1f2d5c')
    cell.get_text().set_color('white')
    cell.get_text().set_fontweight('bold')

# 🔢 Data Cells
for row in range(n_rows):
    for col in range(n_cols):
        value = str(df.iat[row, col])
        table.add_cell(row + 1, col, col_widths[col], cell_height, text=value, loc='center', facecolor='white')

# Render & Save
ax.add_table(table)
plt.savefig("graphs/strategy_metrics.png", dpi=500)
plt.show()
plt.close()
print("✅ PNG file saved as strategy_metrics.png in the graphs directory")
