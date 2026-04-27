"""Quick sensitivity sweep to update latency values with new resource-based methodology."""
import subprocess, sys, json, os
from pathlib import Path
import pandas as pd

script = 'src/algorithms/FedSemGNN.py'
configs = [
    ('tau_0.2', {'semantic_threshold': 0.2, 'ewc_lambda': 0.4}),
    ('tau_0.3', {'semantic_threshold': 0.3, 'ewc_lambda': 0.4}),
    ('tau_0.4', {'semantic_threshold': 0.4, 'ewc_lambda': 0.4}),
    ('ewc_0.0', {'semantic_threshold': 0.3, 'ewc_lambda': 0.0}),
    ('ewc_0.4', {'semantic_threshold': 0.3, 'ewc_lambda': 0.4}),
    ('ewc_0.8', {'semantic_threshold': 0.3, 'ewc_lambda': 0.8}),
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
        print(f'  {name}: Latency={lat:.2f}+/-{lat_std:.2f}ms, Fidelity={fid:.1f}+/-{fid_std:.1f}%')
        results.append({'name': name, 'latency': lat, 'lat_std': lat_std, 
                        'fidelity': fid, 'fid_std': fid_std})
    else:
        print(f'  {name}: FAILED')
        if r.stderr:
            print(r.stderr[-500:])

print('\n=== Summary ===')
for r in results:
    print(f"{r['name']}: Lat={r['latency']:.2f}+/-{r['lat_std']:.2f}ms, Fid={r['fidelity']:.2f}+/-{r['fid_std']:.2f}%")
