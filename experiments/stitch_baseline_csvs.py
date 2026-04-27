#stitch_baseline_csvs.py


import os, shutil, glob

# Map baseline‐script output names → FedSemGNN run‐folder pattern
BAS = {
  "FlatFedPPO": "results/flat_fedppo_metrics.csv",
  "HierFedPPO": "results/hier_fedppo_metrics.csv",
  "HSQF": "results/hsqf_metrics.csv",
  "RandomPlacement": "results/random_place_metrics.csv"
}

for algo, src_name in BAS.items():
  for steps in [500, 1000]:
    run_dir = f"results/{algo}_gcn_{steps}steps"
    src     = os.path.join(os.getcwd(), src_name)
    dst     = os.path.join(run_dir, "fedsemgnn_metrics.csv")

    if not os.path.exists(src):
      print(f" ⚠️  Missing {src_name}, skipping {algo} {steps}")
      continue

    os.makedirs(run_dir, exist_ok=True)
    shutil.copy(src, dst)
    print(f"Copied {src_name} → {dst}")
