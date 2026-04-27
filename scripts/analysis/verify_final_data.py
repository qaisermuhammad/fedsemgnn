"""Comprehensive verification of all experimental data."""
import pandas as pd
import os

def summarize(folder, label):
    print(f'\n=== {label} ===')
    algos_order = ['fedsemgnn', 'flat_fedppo', 'centralized_ppo', 'hier_fedppo', 'hsqf', 'random_place']
    print(f'{"Algorithm":<20} {"Rows":>5} {"Nodes":>6} {"AvgLat":>10} {"AvgFid":>8} {"AvgPow":>12} {"TotMig":>10} {"AvgComm":>10} {"AvgRew":>10}')
    print('-' * 92)
    results = {}
    for a in algos_order:
        fp = os.path.join(folder, f'{a}_metrics.csv')
        if os.path.exists(fp):
            df = pd.read_csv(fp)
            r = {
                'rows': len(df),
                'nodes': int(df['Num_Nodes'].iloc[0]),
                'lat': df['Latency_ms'].mean(),
                'fid': df['Fidelity_pct'].mean(),
                'pow': df['Power_W'].mean(),
                'mig': int(df['Migrations'].sum()),
                'comm': df['Bytes_step_MB'].mean(),
                'rew': df['Reward'].mean(),
                'pow_last': df['Power_W'].iloc[-1],
                'pow_first': df['Power_W'].iloc[0],
            }
            results[a] = r
            print(f'{a:<20} {r["rows"]:>5} {r["nodes"]:>6} {r["lat"]:>10.2f} {r["fid"]:>8.2f} {r["pow"]:>12.2f} {r["mig"]:>10} {r["comm"]:>10.4f} {r["rew"]:>10.4f}')
        else:
            print(f'{a:<20} MISSING')
    return results

r6 = summarize('results/6node_results', '6-NODE RESULTS (base scale)')
r200 = summarize('results/200node_results', '200-NODE RESULTS (scalability)')

# Compute comparison ratios
if r6:
    print('\n=== 6-NODE COMPARISON RATIOS (vs FedSemGNN) ===')
    fed = r6.get('fedsemgnn')
    if fed:
        for a, r in r6.items():
            if a != 'fedsemgnn':
                lat_ratio = r['lat'] / fed['lat'] if fed['lat'] > 0 else float('inf')
                comm_ratio = r['comm'] / fed['comm'] if fed['comm'] > 0 else float('inf')
                print(f'  {a}: lat_ratio={lat_ratio:.2f}x, comm_ratio={comm_ratio:.2f}x, fid={r["fid"]:.1f}%')
