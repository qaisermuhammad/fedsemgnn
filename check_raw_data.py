import pandas as pd
import os

algos = ['fedsemgnn', 'flat_fedppo', 'centralized_ppo', 'hier_fedppo', 'hsqf', 'random_place']

print('=== RAW DATA SAMPLE (first 5 + last 5 rows) ===')
for a in algos:
    fp = f'results/{a}_metrics.csv'
    df = pd.read_csv(fp)
    print(f'\n--- {a} (nodes={df["Num_Nodes"].iloc[0]}) ---')
    print('Columns:', list(df.columns))
    # First 3 rows
    for _, row in df.head(3).iterrows():
        print(f'  Step={row["Step"]}: Lat={row["Latency_ms"]:.4f}, Fid={row["Fidelity_pct"]:.2f}, Pow={row["Power_W"]:.2f}, Mig={row["Migrations"]}, Comm={row["Bytes_step_MB"]:.4f}')
    print('  ...')
    # Last 3 rows
    for _, row in df.tail(3).iterrows():
        print(f'  Step={row["Step"]}: Lat={row["Latency_ms"]:.4f}, Fid={row["Fidelity_pct"]:.2f}, Pow={row["Power_W"]:.2f}, Mig={row["Migrations"]}, Comm={row["Bytes_step_MB"]:.4f}')

print('\n=== STATISTICS ===')
print(f'{"Algo":<20} {"Lat_min":>8} {"Lat_max":>8} {"Lat_std":>8} {"Fid_min":>8} {"Fid_max":>8} {"Pow_min":>10} {"Pow_max":>10} {"Mig_min":>10} {"Mig_max":>10}')
for a in algos:
    fp = f'results/{a}_metrics.csv'
    df = pd.read_csv(fp)
    print(f'{a:<20} {df["Latency_ms"].min():>8.2f} {df["Latency_ms"].max():>8.2f} {df["Latency_ms"].std():>8.2f} {df["Fidelity_pct"].min():>8.2f} {df["Fidelity_pct"].max():>8.2f} {df["Power_W"].min():>10.2f} {df["Power_W"].max():>10.2f} {df["Migrations"].min():>10} {df["Migrations"].max():>10}')
