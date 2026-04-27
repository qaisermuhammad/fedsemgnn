"""Extract precise paper-ready metrics from 6-node data."""
import pandas as pd
import os

print('=== PRECISE 6-NODE METRICS FOR PAPER ===\n')
algos = ['fedsemgnn', 'flat_fedppo', 'centralized_ppo', 'hier_fedppo', 'hsqf', 'random_place']
folder = 'results/6node_results'

data = {}
for a in algos:
    fp = os.path.join(folder, f'{a}_metrics.csv')
    df = pd.read_csv(fp)
    # Total communication = sum of per-step bytes
    total_comm = df['Bytes_step_MB'].sum()
    # Or check Bytes_cum_MB at last step
    cum_comm = df['Bytes_cum_MB'].iloc[-1] if 'Bytes_cum_MB' in df.columns else total_comm
    
    data[a] = {
        'lat': df['Latency_ms'].mean(),
        'fid': df['Fidelity_pct'].mean(),
        'pow': df['Power_W'].mean(),
        'mig_total': int(df['Migrations'].sum()),
        'mig_last': int(df['Migrations'].iloc[-1]),
        'comm_total_sum': total_comm,
        'comm_cum_last': cum_comm,
        'rew': df['Reward'].mean(),
        'pow_first': df['Power_W'].iloc[0],
        'pow_last': df['Power_W'].iloc[-1],
    }

for a, d in data.items():
    print(f'{a}:')
    print(f'  Latency:      {d["lat"]:.2f} ms')
    print(f'  Fidelity:     {d["fid"]:.2f}%')
    print(f'  Power(avg):   {d["pow"]:.2f} W')
    print(f'  Pow(first):   {d["pow_first"]:.2f} W  Pow(last): {d["pow_last"]:.2f} W')
    print(f'  Migrations:   total_sum={d["mig_total"]}, last_step={d["mig_last"]}')
    print(f'  Comm(sum):    {d["comm_total_sum"]:.4f} MB')
    print(f'  Comm(cum):    {d["comm_cum_last"]:.4f} MB')
    print(f'  Reward(avg):  {d["rew"]:.4f}')
    print()

# Comparison ratios
fed = data['fedsemgnn']
print('=== COMPARISON RATIOS (vs FedSemGNN) ===\n')
for a, d in data.items():
    if a != 'fedsemgnn':
        lat_ratio = d['lat'] / fed['lat'] if fed['lat'] > 0 else 0
        comm_fed = max(fed['comm_cum_last'], fed['comm_total_sum'])
        comm_other = max(d['comm_cum_last'], d['comm_total_sum'])
        comm_ratio = comm_other / comm_fed if comm_fed > 0 else 0
        pow_ratio = d['pow'] / fed['pow'] if fed['pow'] > 0 else 0
        print(f'  {a}:')
        print(f'    latency ratio: {lat_ratio:.2f}x (FedSemGNN is {lat_ratio:.1f}x faster)')
        print(f'    comm ratio:    {comm_ratio:.2f}x (FedSemGNN comm is {comm_ratio:.1f}x lower)')
        print(f'    power ratio:   {pow_ratio:.2f}x (FedSemGNN power is {pow_ratio:.1f}x lower)')
        print()

# Per-node power for scalability
print('=== 200-NODE SCALABILITY ===\n')
folder200 = 'results/200node_results'
for a in algos:
    fp = os.path.join(folder200, f'{a}_metrics.csv')
    if os.path.exists(fp):
        df = pd.read_csv(fp) 
        per_node = df['Power_W'].iloc[0] / 200  # First step power / nodes
        print(f'  {a}: 200-node first_step_pow={df["Power_W"].iloc[0]:.2f}W, per_node={per_node:.2f}W/node')

# FedSemGNN per-node power at 6 vs 200
fed6_pn = data['fedsemgnn']['pow_first'] / 6
fed200 = pd.read_csv(os.path.join(folder200, 'fedsemgnn_metrics.csv'))
fed200_pn = fed200['Power_W'].iloc[0] / 200
print(f'\n  FedSemGNN per-node: 6-node={fed6_pn:.2f}W/node, 200-node={fed200_pn:.2f}W/node')
