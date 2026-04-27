import pandas as pd
import os

print('=== 6-NODE BACKUP STATUS ===')
folder = 'results/6node_backup'
if os.path.exists(folder):
    for f in sorted(os.listdir(folder)):
        if f.endswith('.csv'):
            df = pd.read_csv(os.path.join(folder, f))
            print(f'  {f}: rows={len(df)}, cols={list(df.columns[:8])}')
            if len(df) > 0:
                print(f'     Num_Nodes col? {"Num_Nodes" in df.columns}')
                if 'Num_Nodes' in df.columns:
                    print(f'     nodes={df["Num_Nodes"].iloc[0]}')
else:
    print('  6node_backup folder does not exist!')

# Check if there are any other 6-node CSV files around
print('\n=== CHECKING FOR 6-NODE DATA ELSEWHERE ===')
for fname in ['flat_fedppo_metrics.csv']:
    for path in ['results/', 'results/6node_backup/']:
        fp = os.path.join(path, fname)
        if os.path.exists(fp):
            df = pd.read_csv(fp)
            print(f'  {path}{fname}: rows={len(df)}, first_cols={list(df.columns[:6])}')
