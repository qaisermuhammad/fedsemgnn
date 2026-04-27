# run_experiments.py
import os, sys, subprocess, shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--steps", type=int, default=None)
parser.add_argument("--algo", choices=["FedSemGNN","FlatFedPPO","HierFedPPO","HSQF","RandomPlacement"], default=None)
parser.add_argument("--encoder", choices=["gcn","linear"], default=None)
parser.add_argument("--output-dir", default=None)
args, unknown = parser.parse_known_args()


PYTHON = sys.executable

STEPS    = [args.steps] if args.steps else [500, 1000]
ALGOS    = [args.algo] if args.algo else ["FedSemGNN","FlatFedPPO","HierFedPPO","HSQF","RandomPlacement"]
ENCODERS = [args.encoder] if args.encoder else ["gcn","linear"]



# Map each baseline to its script name and its default CSV output
BASELINE_INFO = {
    "FlatFedPPO":      (os.path.join("src", "algorithms", "flat_fedppo.py"),    "results/flat_fedppo_metrics.csv"),
    "HierFedPPO":      (os.path.join("src", "algorithms", "hier_fedppo.py"),    "results/hier_fedppo_metrics.csv"),
    "HSQF":            (os.path.join("src", "algorithms", "hsqf.py"),           "results/hsqf_metrics.csv"),
    "RandomPlacement": (os.path.join("src", "algorithms", "random_place.py"),   "results/random_place_metrics.csv"),
}

for steps in STEPS:
    for algo in ALGOS:
        for enc in ENCODERS:
            # linear encoder only makes sense for FedSemGNN
            if algo != "FedSemGNN" and enc != "gcn":
                continue

            run_dir = f"results/{algo}_{enc}_{steps}steps"
            if args.output_dir:
                run_dir = args.output_dir

            os.makedirs(run_dir, exist_ok=True)
            print(f"→ {algo} | encoder={enc} | steps={steps}")


            fedsemgnn_path = os.path.join("src", "algorithms", "FedSemGNN.py")
            if not os.path.exists(fedsemgnn_path):
                fedsemgnn_path = os.path.join("algorithms", "FedSemGNN.py")
            cmd = [
                PYTHON, fedsemgnn_path,
                "--steps",             str(steps),
                "--encoder",           enc,
                "--output-dir",        run_dir
            ]
            # Only pass --algo if supported
            if algo != "FedSemGNN":
                cmd += ["--algo", algo]

            subprocess.run(cmd, check=True)

            # 2) move its output CSV into the FedSemGNN run-folder (FedSemGNN only)
            if algo == "FedSemGNN":
                dst = os.path.join(run_dir, "fedsemgnn_metrics.csv")
                src = os.path.join(run_dir, "fedsemgnn_metrics.csv")
                if os.path.exists(src):
                    shutil.move(src, dst)
                else:
                    print(f"⚠️  Expected {src} not found!")

            print(f"✅ Done {algo} @ {steps} steps → {run_dir}")
