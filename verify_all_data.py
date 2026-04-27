import pandas as pd
import os

print('=== ALL 6 ALGORITHM CSVs (main results/) ===')
algos = ['fedsemgnn', 'flat_fedppo', 'centralized_ppo', 'hier_fedppo', 'hsqf', 'random_place']
for a in algos:
    fp = f'results/{a}_metrics.csv'
    if os.path.exists(fp):
        df = pd.read_csv(fp)
        nodes = df['Num_Nodes'].iloc[0]
        rows = len(df)
        avg_lat = df['Latency_ms'].mean()
        avg_fid = df['Fidelity_pct'].mean()
        avg_pow = df['Power_W'].mean()
        tot_mig = df['Migrations'].sum()
        avg_comm = df['Bytes_step_MB'].mean()
        avg_rew = df['Reward'].mean()
        last_step = df['Step'].iloc[-1]
        print(f'  {a}: rows={rows}, nodes={nodes}, step_last={last_step}')
        print(f'    Lat={avg_lat:.2f}ms, Fid={avg_fid:.2f}%, Pow={avg_pow:.2f}W, Mig={tot_mig}, Comm={avg_comm:.4f}MB, Reward={avg_rew:.4f}')
    else:
        print(f'  {a}: MISSING')

print()
print('=== 200-NODE RESULTS COPIES ===')
folder = 'results/200node_results'
for f in sorted(os.listdir(folder)):
    if f.endswith('.csv'):
        df = pd.read_csv(os.path.join(folder, f))
        nodes = df['Num_Nodes'].iloc[0]
        rows = len(df)
        print(f'  {f}: rows={rows}, nodes={nodes}')

print()
print('=== DATA SUMMARY TABLE (200-node) ===')
print(f'{"Algorithm":<20} {"Lat(ms)":<10} {"Fid(%)":<10} {"Power(W)":<12} {"TotMig":<10} {"Comm(MB)":<12} {"Reward":<10}')
print('-' * 84)
for a in algos:
    fp = f'results/{a}_metrics.csv'
    if os.path.exists(fp):
        df = pd.read_csv(fp)
        if df['Num_Nodes'].iloc[0] == 200:
            print(f'{a:<20} {df["Latency_ms"].mean():<10.2f} {df["Fidelity_pct"].mean():<10.2f} {df["Power_W"].mean():<12.2f} {df["Migrations"].sum():<10} {df["Bytes_step_MB"].mean():<12.4f} {df["Reward"].mean():<10.4f}')
        else:
            print(f'{a:<20} WRONG NODE COUNT: {df["Num_Nodes"].iloc[0]}')
