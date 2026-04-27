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

for name, f in files.items():
    df = pd.read_csv(f)
    print(f"\n=== {name} ({len(df)} steps) ===")
    print(f"  Reward: mean={df['Reward'].mean():.4f}, std={df['Reward'].std():.4f}, sem={df['Reward'].sem():.4f}")
    print(f"  Latency_ms: mean={df['Latency_ms'].mean():.4f}, std={df['Latency_ms'].std():.4f}")
    print(f"  Fidelity_pct: mean={df['Fidelity_pct'].mean():.4f}, std={df['Fidelity_pct'].std():.4f}")
    print(f"  Power_W: mean={df['Power_W'].mean():.4f}, std={df['Power_W'].std():.4f}")
    print(f"  Migrations total: {df['Migrations'].sum()}")
    if 'Bytes_cum_MB' in df.columns:
        print(f"  Bytes_cum_MB final: {df['Bytes_cum_MB'].iloc[-1]:.4f}")
    print(f"  Num_Nodes: {df['Num_Nodes'].iloc[0]}")
    
    # Efficiency: final_reward / final_bytes
    if 'Bytes_cum_MB' in df.columns:
        fb = df['Bytes_cum_MB'].iloc[-1]
        fr = df['Reward'].iloc[-1]
        eff = fr / fb if fb > 0 else 0
        print(f"  Efficiency (reward/MB): {eff:.4f}")

# Comparison ratios
print("\n\n=== KEY COMPARISONS (paper claims) ===")
fed = pd.read_csv('results/fedsemgnn_metrics.csv')
flat = pd.read_csv('results/flat_fedppo_metrics.csv')
hier = pd.read_csv('results/hier_fedppo_metrics.csv')
hsqf = pd.read_csv('results/hsqf_metrics.csv')
rand = pd.read_csv('results/random_place_metrics.csv')
cent = pd.read_csv('results/centralized_ppo_metrics.csv')

print(f"\nFedSemGNN reward mean: {fed['Reward'].mean():.4f}")
print(f"FlatFedPPO reward mean: {flat['Reward'].mean():.4f}")
print(f"Reward ratio FedSem/Flat: {fed['Reward'].mean()/flat['Reward'].mean():.4f}")

print(f"\nLatency ratios:")
print(f"  FedSem: {fed['Latency_ms'].mean():.4f} ms")
print(f"  Flat: {flat['Latency_ms'].mean():.4f} ms")
print(f"  Hier: {hier['Latency_ms'].mean():.4f} ms")
print(f"  HSQF: {hsqf['Latency_ms'].mean():.4f} ms")
print(f"  Random: {rand['Latency_ms'].mean():.4f} ms")
print(f"  Centralized: {cent['Latency_ms'].mean():.4f} ms")
print(f"  Flat/FedSem ratio: {flat['Latency_ms'].mean()/fed['Latency_ms'].mean():.1f}x")

print(f"\nPower ratios:")
print(f"  FedSem: {fed['Power_W'].mean():.2f} W")
print(f"  Flat: {flat['Power_W'].mean():.2f} W")
print(f"  Flat/FedSem ratio: {flat['Power_W'].mean()/fed['Power_W'].mean():.1f}x")

print(f"\nBytes final:")
for name, f in files.items():
    df = pd.read_csv(f)
    if 'Bytes_cum_MB' in df.columns:
        print(f"  {name}: {df['Bytes_cum_MB'].iloc[-1]:.4f} MB")

print(f"\nMigrations:")
for name, f in files.items():
    df = pd.read_csv(f)
    print(f"  {name}: {df['Migrations'].sum()}")

print(f"\nFidelity:")
for name, f in files.items():
    df = pd.read_csv(f)
    print(f"  {name}: {df['Fidelity_pct'].mean():.2f}%")

# Comm efficiency
print(f"\nComm Efficiency (reward/MB):")
for name, f in files.items():
    df = pd.read_csv(f)
    if 'Bytes_cum_MB' in df.columns:
        fb = df['Bytes_cum_MB'].iloc[-1]
        fr = df['Reward'].iloc[-1]
        eff = fr / fb if fb > 0 else 0
        print(f"  {name}: {eff:.4f}")
