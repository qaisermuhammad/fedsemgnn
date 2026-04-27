import pandas as pd

# The key test: if ALL algorithms ran on the same 6-node topology,
# their Migrations per step should be bounded by the actual server count.
# With 6 servers, the max possible migrations per step can't exceed the number of services.

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
    # Check max migrations per step - if truly 10000 nodes we'd expect much higher
    print(f"{name}: Num_Nodes_reported={df['Num_Nodes'].iloc[0]}, "
          f"Max_Migration/step={df['Migrations'].max()}, "
          f"Avg_Migration/step={df['Migrations'].mean():.1f}, "
          f"Power_std={df['Power_W'].std():.1f}, "
          f"Latency_std={df['Latency_ms'].std():.2f}")

# Also check: what's the base dataset?
import json
import os
for path in ['workloads/sample_dataset3.json', 'workloads/sample_dataset.json']:
    if os.path.exists(path):
        with open(path, 'r') as fi:
            data = json.load(fi)
        servers = data.get('EdgeServer', [])
        services = data.get('Service', [])
        users = data.get('User', [])
        print(f"\nDataset: {path}")
        print(f"  EdgeServers: {len(servers)}")
        print(f"  Services: {len(services)}")
        print(f"  Users: {len(users)}")
