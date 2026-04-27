"""Collect results from all 6 fresh CSV files and compute Table 2 statistics."""
import csv
import statistics

files = {
    'FedSemGNN': 'results/fedsemgnn_metrics.csv',
    'FlatFedPPO': 'results/flat_fedppo_metrics.csv',
    'CentralizedPPO': 'results/centralized_ppo_metrics.csv',
    'HierFedPPO': 'results/hier_fedppo_metrics.csv',
    'HSQF': 'results/hsqf_metrics.csv',
    'Random': 'results/random_place_metrics.csv'
}

print('=' * 120)
header = f"{'Algorithm':<16} {'Rows':>5} {'Mean Reward':>12} {'Mean Lat(ms)':>13} {'Mean Fid(%)':>12} {'Mean Pwr(W)':>12} {'Tot Mig':>8} {'Max Cum MB':>11} {'Nodes':>6}"
print(header)
print('=' * 120)

all_data = {}
for name, fpath in files.items():
    with open(fpath, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    rewards = [float(r['Reward']) for r in rows]
    latencies = [float(r['Latency_ms']) for r in rows]
    fidelities = [float(r['Fidelity_pct']) for r in rows]
    powers = [float(r['Power_W']) for r in rows]
    migrations = [int(r['Migrations']) for r in rows]
    bytes_cum = [float(r['Bytes_cum_MB']) for r in rows]
    nodes = set(int(r['Num_Nodes']) for r in rows)
    
    mean_reward = statistics.mean(rewards)
    mean_lat = statistics.mean(latencies)
    mean_fid = statistics.mean(fidelities)
    mean_pwr = statistics.mean(powers)
    tot_mig = sum(migrations)
    max_cum = max(bytes_cum)
    
    all_data[name] = {
        'rows': len(rows),
        'reward': mean_reward,
        'latency': mean_lat,
        'fidelity': mean_fid,
        'power': mean_pwr,
        'migrations': tot_mig,
        'bytes': max_cum,
        'nodes': nodes
    }
    
    print(f"{name:<16} {len(rows):>5} {mean_reward:>12.4f} {mean_lat:>13.2f} {mean_fid:>12.2f} {mean_pwr:>12.2f} {tot_mig:>8} {max_cum:>11.2f} {nodes}")

print()
print('--- Relative Comparisons (FedSemGNN vs others) ---')
fed = all_data['FedSemGNN']
for name in ['FlatFedPPO', 'CentralizedPPO', 'HierFedPPO', 'HSQF', 'Random']:
    other = all_data[name]
    print(f"\nFedSemGNN vs {name}:")
    if other['reward'] != 0:
        improvement = ((fed['reward'] - other['reward']) / abs(other['reward'])) * 100
        print(f"  Reward: {fed['reward']:.4f} vs {other['reward']:.4f} (improvement: {improvement:.1f}%)")
    lat_reduction = ((other['latency'] - fed['latency']) / other['latency']) * 100
    print(f"  Latency: {fed['latency']:.2f} vs {other['latency']:.2f} (reduction: {lat_reduction:.1f}%)")
    print(f"  Fidelity: {fed['fidelity']:.2f}% vs {other['fidelity']:.2f}%")
    pwr_reduction = ((other['power'] - fed['power']) / other['power']) * 100
    print(f"  Power: {fed['power']:.2f} vs {other['power']:.2f} (reduction: {pwr_reduction:.1f}%)")
    print(f"  Migrations: {fed['migrations']} vs {other['migrations']}")
    print(f"  Bytes: {fed['bytes']:.2f} vs {other['bytes']:.2f}")
    if other['bytes'] != 0:
        fed_eff = fed['reward'] / fed['bytes'] if fed['bytes'] != 0 else 0
        oth_eff = other['reward'] / other['bytes'] if other['bytes'] != 0 else 0
        print(f"  Comm. Efficiency (Reward/MB): {fed_eff:.4f} vs {oth_eff:.4f}")

print()
print('--- Communication Efficiency ---')
for name, d in all_data.items():
    eff = d['reward'] / d['bytes'] if d['bytes'] != 0 else 0
    print(f"  {name}: {eff:.4f} reward/MB (reward={d['reward']:.4f}, bytes={d['bytes']:.2f}MB)")

# Also print values rounded for LaTeX table
print()
print('--- LaTeX Table Values (rounded) ---')
for name, d in all_data.items():
    reward_str = f"{d['reward']:.3f}"
    lat_str = f"{d['latency']:.2f}"
    fid_str = f"{d['fidelity']:.1f}"
    pwr_str = f"{d['power']:.1f}"
    mig_str = str(d['migrations'])
    bytes_str = f"{d['bytes']:.2f}"
    print(f"  {name}: Reward={reward_str}, Lat={lat_str}, Fid={fid_str}, Pwr={pwr_str}, Mig={mig_str}, Bytes={bytes_str}")
