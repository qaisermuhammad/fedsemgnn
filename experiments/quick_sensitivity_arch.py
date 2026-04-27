"""Quick architectural parameter sensitivity sweep."""
import subprocess, sys, json, os
from pathlib import Path
import pandas as pd

script = 'src/algorithms/FedSemGNN.py'
configs = [
    ('dim_8',  {'semantic_dim': 8}),
    ('dim_16', {'semantic_dim': 16}),
    ('dim_32', {'semantic_dim': 32}),
    ('k1_5',   {'local_sync_interval': 5}),
    ('k1_10',  {'local_sync_interval': 10}),
    ('k1_20',  {'local_sync_interval': 20}),
    ('buf_10k', {'replay_buffer_capacity': 10000}),
    ('buf_20k', {'replay_buffer_capacity': 20000}),
    ('buf_40k', {'replay_buffer_capacity': 40000}),
]

os.chdir(Path(__file__).resolve().parents[1])
results = []
for name, cfg in configs:
    print(f'\n=== Running {name} ===')
    cfg_path = Path(f'results/sensitivity/{name}/config.json')
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(cfg))
    
    metrics_path = Path('results/fedsemgnn_metrics.csv')
    if metrics_path.exists():
        metrics_path.unlink()
    
    cmd = [sys.executable, script, '--steps', '50', '--override-num-nodes', '100',
           '--config-override', str(cfg_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    
    if metrics_path.exists():
        df = pd.read_csv(metrics_path)
        lat = df['Latency_ms'].mean()
        fid = df['Fidelity_pct'].mean()
        lat_std = df['Latency_ms'].std()
        fid_std = df['Fidelity_pct'].std()
        print(f'  {name}: Lat={lat:.2f}+/-{lat_std:.2f}ms, Fid={fid:.1f}+/-{fid_std:.1f}%')
        results.append({'name': name, 'latency': lat, 'lat_std': lat_std,
                        'fidelity': fid, 'fid_std': fid_std})
    else:
        print(f'  {name}: FAILED')
        if r.stderr:
            print(r.stderr[-500:])

print('\n=== Summary ===')
for r in results:
    print(f"{r['name']}: Lat={r['latency']:.2f}+/-{r['lat_std']:.2f}ms, Fid={r['fidelity']:.2f}+/-{r['fid_std']:.2f}%")
