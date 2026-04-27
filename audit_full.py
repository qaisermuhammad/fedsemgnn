import pandas as pd
import numpy as np

files = {
    'FedSemGNN': 'results/fedsemgnn_metrics.csv',
    'FlatFedPPO': 'results/flat_fedppo_metrics.csv',
    'HierFedPPO': 'results/hier_fedppo_metrics.csv',
    'HSQF': 'results/hsqf_metrics.csv',
    'RandomPlacement': 'results/random_place_metrics.csv',
    'CentralizedPPO': 'results/centralized_ppo_metrics.csv',
}

print("="*80)
print("COMPREHENSIVE PAPER AUDIT: CSV Data vs Paper Claims")
print("="*80)

# 1. Check Num_Nodes
print("\n1. NODE SCALE CHECK (CRITICAL)")
print("-"*40)
for name, f in files.items():
    df = pd.read_csv(f)
    nodes = df['Num_Nodes'].unique()
    print(f"  {name}: Num_Nodes = {nodes}")

# 2. CSV column headers
print("\n2. CSV COLUMNS")
print("-"*40)
df0 = pd.read_csv('results/fedsemgnn_metrics.csv')
print(f"  Columns: {list(df0.columns)}")

# 3. Full per-algorithm summary
print("\n3. COMPLETE METRICS SUMMARY")
print("-"*80)
print(f"{'Metric':<25} {'FedSemGNN':>12} {'FlatFedPPO':>12} {'HierFedPPO':>12} {'HSQF':>12} {'Random':>12} {'Central':>12}")
print("-"*97)

all_data = {}
for name, f in files.items():
    all_data[name] = pd.read_csv(f)

# Reward mean
print(f"{'Reward mean':<25}", end='')
for name in ['FedSemGNN','FlatFedPPO','HierFedPPO','HSQF','RandomPlacement','CentralizedPPO']:
    print(f" {all_data[name]['Reward'].mean():>11.4f}", end='')
print()

# Latency mean
print(f"{'Latency_ms mean':<25}", end='')
for name in ['FedSemGNN','FlatFedPPO','HierFedPPO','HSQF','RandomPlacement','CentralizedPPO']:
    print(f" {all_data[name]['Latency_ms'].mean():>11.4f}", end='')
print()

# Fidelity mean
print(f"{'Fidelity_pct mean':<25}", end='')
for name in ['FedSemGNN','FlatFedPPO','HierFedPPO','HSQF','RandomPlacement','CentralizedPPO']:
    print(f" {all_data[name]['Fidelity_pct'].mean():>11.2f}", end='')
print()

# Power mean
print(f"{'Power_W mean':<25}", end='')
for name in ['FedSemGNN','FlatFedPPO','HierFedPPO','HSQF','RandomPlacement','CentralizedPPO']:
    print(f" {all_data[name]['Power_W'].mean():>11.2f}", end='')
print()

# Migrations total
print(f"{'Migrations total':<25}", end='')
for name in ['FedSemGNN','FlatFedPPO','HierFedPPO','HSQF','RandomPlacement','CentralizedPPO']:
    print(f" {all_data[name]['Migrations'].sum():>11d}", end='')
print()

# Bytes final
print(f"{'Bytes_cum_MB final':<25}", end='')
for name in ['FedSemGNN','FlatFedPPO','HierFedPPO','HSQF','RandomPlacement','CentralizedPPO']:
    if 'Bytes_cum_MB' in all_data[name].columns:
        print(f" {all_data[name]['Bytes_cum_MB'].iloc[-1]:>11.4f}", end='')
    else:
        print(f" {'N/A':>11}", end='')
print()

# Num_Nodes
print(f"{'Num_Nodes':<25}", end='')
for name in ['FedSemGNN','FlatFedPPO','HierFedPPO','HSQF','RandomPlacement','CentralizedPPO']:
    print(f" {all_data[name]['Num_Nodes'].iloc[0]:>11d}", end='')
print()

# 4. Paper Table II comparison
print("\n\n4. PAPER TABLE II VS ACTUAL DATA")
print("="*97)
paper = {
    'Reward':   {'FedSemGNN': 0.91, 'FlatFedPPO': 0.84, 'HierFedPPO': 0.78, 'HSQF': 0.69, 'Random': 0.31},
    'Latency':  {'FedSemGNN': 0.36, 'FlatFedPPO': 114.25, 'HierFedPPO': 80.71, 'HSQF': 45.82, 'Random': 112.50},
    'Fidelity': {'FedSemGNN': 100.0, 'FlatFedPPO': 84.2, 'HierFedPPO': 79.1, 'HSQF': 91.3, 'Random': 62.4},
    'Power':    {'FedSemGNN': 72.1, 'FlatFedPPO': 2607.9, 'HierFedPPO': 1057.4, 'HSQF': 534.7, 'Random': None},
    'Migrations':{'FedSemGNN': 0, 'FlatFedPPO': 6840, 'HierFedPPO': 1181, 'HSQF': 342, 'Random': 4521},
    'Bytes':    {'FedSemGNN': 0.65, 'FlatFedPPO': 105.0, 'HierFedPPO': 32.5, 'HSQF': 16.4, 'Random': None},
}
actual_map = {'Random': 'RandomPlacement'}

for metric in paper:
    print(f"\n  --- {metric} ---")
    for algo, paper_val in paper[metric].items():
        csv_name = actual_map.get(algo, algo)
        if paper_val is None:
            print(f"  {algo}: Paper=N/A")
            continue
        if metric == 'Reward':
            csv_val = all_data[csv_name]['Reward'].mean()
        elif metric == 'Latency':
            csv_val = all_data[csv_name]['Latency_ms'].mean() 
        elif metric == 'Fidelity':
            csv_val = all_data[csv_name]['Fidelity_pct'].mean()
        elif metric == 'Power':
            csv_val = all_data[csv_name]['Power_W'].mean()
        elif metric == 'Migrations':
            csv_val = all_data[csv_name]['Migrations'].sum()
        elif metric == 'Bytes':
            csv_val = all_data[csv_name]['Bytes_cum_MB'].iloc[-1] if 'Bytes_cum_MB' in all_data[csv_name].columns else 0
        
        if isinstance(paper_val, float):
            ratio = csv_val / paper_val if paper_val != 0 else float('inf')
            match = abs(ratio - 1.0) < 0.10  # within 10%
            print(f"  {algo}: Paper={paper_val}, CSV={csv_val:.4f}, Ratio={ratio:.2f}x {'OK' if match else '*** MISMATCH ***'}")
        else:
            match = abs(csv_val - paper_val) / max(abs(paper_val), 1) < 0.10
            print(f"  {algo}: Paper={paper_val}, CSV={csv_val:.0f}, {'OK' if match else '*** MISMATCH ***'}")

# 5. Paper ratio claims
print("\n\n5. PAPER RATIO CLAIMS VS ACTUAL")
print("="*80)
fed = all_data['FedSemGNN']
flat = all_data['FlatFedPPO']
hier = all_data['HierFedPPO']

lat_ratio = flat['Latency_ms'].mean() / fed['Latency_ms'].mean()
print(f"  Paper: '315x faster than FlatFedPPO'")
print(f"  Actual: {lat_ratio:.1f}x   *** {'OK' if abs(lat_ratio - 315) < 30 else 'MISMATCH: ' + str(round(lat_ratio,1)) + 'x'} ***")

pow_ratio = flat['Power_W'].mean() / fed['Power_W'].mean()
print(f"\n  Paper: '36.2x lower power than FlatFedPPO'")
print(f"  Actual: {pow_ratio:.1f}x   *** {'OK' if abs(pow_ratio - 36.2) < 5 else 'MISMATCH: ' + str(round(pow_ratio,1)) + 'x'} ***")

bytes_ratio = flat['Bytes_cum_MB'].iloc[-1] / fed['Bytes_cum_MB'].iloc[-1] if fed['Bytes_cum_MB'].iloc[-1] > 0 else 0
print(f"\n  Paper: '161x communication reduction'")
print(f"  Actual: {bytes_ratio:.1f}x   *** {'OK' if abs(bytes_ratio - 161) < 20 else 'MISMATCH: ' + str(round(bytes_ratio,1)) + 'x'} ***")

print(f"\n  Paper: 'Latency 0.36 ms'")
print(f"  Actual: {fed['Latency_ms'].mean():.2f} ms   *** MISMATCH ({fed['Latency_ms'].mean()/0.36:.0f}x off) ***")

print(f"\n  Paper: 'Power 72.1 W'")
print(f"  Actual: {fed['Power_W'].mean():.1f} W   *** MISMATCH ({fed['Power_W'].mean()/72.1:.0f}x off) ***")

print(f"\n  Paper: 'Zero migrations'")
print(f"  Actual: {fed['Migrations'].sum()} migrations   *** MISMATCH ***")

# 6. Ranking check
print("\n\n6. ACTUAL REWARD RANKING (Is FedSemGNN really #1?)")
print("="*80)
rewards = {name: all_data[name]['Reward'].mean() for name in all_data}
for rank, (name, val) in enumerate(sorted(rewards.items(), key=lambda x: -x[1]), 1):
    marker = " <<< FedSemGNN IS RANK #" + str(rank) if name == 'FedSemGNN' else ""
    print(f"  #{rank}: {name:<20} mean_reward = {val:.4f}{marker}")
