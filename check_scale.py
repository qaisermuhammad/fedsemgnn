import pandas as pd

files = [
    ('FedSemGNN', 'results/fedsemgnn_metrics.csv'),
    ('FlatFedPPO', 'results/flat_fedppo_metrics.csv'),
    ('HierFedPPO', 'results/hier_fedppo_metrics.csv'),
    ('HSQF', 'results/hsqf_metrics.csv'),
    ('RandomPlacement', 'results/random_place_metrics.csv'),
    ('CentralizedPPO', 'results/centralized_ppo_metrics.csv'),
]

# Check if the --use-generated-topology was used for baselines
# If it was, baselines actually have 10000 servers; if not, they also have 6 but report 10000
for name, f in files:
    df = pd.read_csv(f)
    # Check if Num_Nodes is constant
    unique_nodes = df['Num_Nodes'].unique()
    # Check power range (6 servers vs 10000 servers would have very different ranges)
    print(f"{name}: Num_Nodes_unique={unique_nodes}, Power range=[{df['Power_W'].min():.1f}, {df['Power_W'].max():.1f}], "
          f"Latency range=[{df['Latency_ms'].min():.2f}, {df['Latency_ms'].max():.2f}], "
          f"Migrations range=[{df['Migrations'].min()}, {df['Migrations'].max()}]")
