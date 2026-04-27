"""Verify all numbers in paper against CSV data."""
import pandas as pd, os, math

results = "D:/FedSemGNN/results"

# --- 1. Load all 6 algorithm CSVs ---
algos = {
    "FedSemGNN":     "fedsemgnn_metrics.csv",
    "FlatFedPPO":    "flat_fedppo_metrics.csv",
    "HierFedPPO":    "hier_fedppo_metrics.csv",
    "HSQF":          "hsqf_metrics.csv",
    "RandomPlace":   "random_place_metrics.csv",
    "CentralizedPPO":"centralized_ppo_metrics.csv",
}

print("="*80)
print("SECTION 1: CSV METADATA")
print("="*80)
for name, fn in algos.items():
    fp = os.path.join(results, fn)
    if not os.path.exists(fp):
        print(f"  {name}: FILE NOT FOUND ({fp})")
        continue
    df = pd.read_csv(fp)
    nn = df["Num_Nodes"].iloc[0] if "Num_Nodes" in df.columns else "N/A"
    print(f"  {name}: {len(df)} rows, Num_Nodes={nn}, columns={list(df.columns[:8])}")

# --- 2. Compute aggregated metrics for each algorithm ---
print("\n" + "="*80)
print("SECTION 2: AGGREGATED METRICS (mean over all rows)")
print("="*80)
print(f"{'Algo':20s} {'Reward':>10s} {'Latency':>10s} {'Fidelity':>10s} {'Power':>10s} {'Migr':>10s} {'Bytes(MB)':>10s}")

paper_values = {
    "FedSemGNN":      {"reward": -0.0516, "norm_reward": 0.615, "latency": 41.86, "fidelity": 100.0, "power": 2157, "migr": 41850, "bytes": 0.72},
    "FlatFedPPO":     {"reward": 0.2333,  "norm_reward": 0.812, "latency": 127.19,"fidelity": 67.5,  "power": 2926, "migr": 90428, "bytes": 15.02},
    "HierFedPPO":     {"reward": 0.5063,  "norm_reward": 1.000, "latency": 81.47, "fidelity": 98.4,  "power": 1065, "migr": 11981, "bytes": 207.65},
    "HSQF":           {"reward": -0.9426, "norm_reward": 0.000, "latency": 134.70,"fidelity": 100.0, "power": 840,  "migr": 26941, "bytes": 2.93},
    "RandomPlace":    {"reward": -0.0666, "norm_reward": 0.605, "latency": 119.11,"fidelity": 100.0, "power": 2961, "migr": 89441, "bytes": 0.0019},
    "CentralizedPPO": {"reward": 0.2369,  "norm_reward": 0.814, "latency": 129.70,"fidelity": 72.5,  "power": 3021, "migr": 91420, "bytes": 0.0},
}

computed = {}
for name, fn in algos.items():
    fp = os.path.join(results, fn)
    if not os.path.exists(fp):
        continue
    df = pd.read_csv(fp)
    avg_r = df["Reward"].mean()
    avg_l = df["Latency_ms"].mean()
    avg_f = df["Fidelity_pct"].mean()
    avg_p = df["Power_W"].mean()
    last_migr = df["Migrations"].iloc[-1]
    last_bytes = df["Bytes_cum_MB"].iloc[-1]
    computed[name] = {"reward": avg_r, "latency": avg_l, "fidelity": avg_f, "power": avg_p, "migr": last_migr, "bytes": last_bytes}
    print(f"  {name:20s} {avg_r:10.4f} {avg_l:10.2f} {avg_f:10.1f} {avg_p:10.2f} {last_migr:10.0f} {last_bytes:10.4f}")

# --- 3. Compare computed vs paper ---
print("\n" + "="*80)
print("SECTION 3: DISCREPANCIES (paper vs computed)")
print("="*80)
issues = []
for name in algos:
    if name not in computed or name not in paper_values:
        continue
    pv = paper_values[name]
    cv = computed[name]
    for metric in ["latency", "fidelity", "power", "migr", "bytes"]:
        p = pv[metric]
        c = cv[metric]
        if p == 0 and c == 0:
            continue
        denom = max(abs(p), 0.001)
        pct_diff = abs(p - c) / denom * 100
        if pct_diff > 5:  # flag >5% discrepancy
            issues.append(f"  {name:20s} {metric:10s}: paper={p}, CSV={c:.4f}, diff={pct_diff:.1f}%")
            print(f"  !! {name:20s} {metric:10s}: paper={p}, CSV={c:.4f}, diff={pct_diff:.1f}%")
        else:
            print(f"  OK {name:20s} {metric:10s}: paper={p}, CSV={c:.4f}, diff={pct_diff:.1f}%")

if not issues:
    print("  >>> ALL VALUES MATCH WITHIN 5% TOLERANCE <<<")
else:
    print(f"\n  >>> {len(issues)} DISCREPANCIES FOUND <<<")

# --- 4. Scalability CSV ---
print("\n" + "="*80)
print("SECTION 4: SCALABILITY DATA")
print("="*80)
sc = pd.read_csv(os.path.join(results, "scalability", "scalability_results.csv"))
print(sc.to_string(index=False))

# Paper claims for scalability:
paper_scale = {
    6:    {"lat": 41.86, "power": 2802, "w_node": 467.0, "time": 0.090, "fid": 100},
    25:   {"lat": 31.40, "power": 7937, "w_node": 317.5, "time": 0.100, "fid": 100},
    50:   {"lat": 29.83, "power": 14296,"w_node": 285.9, "time": 0.120, "fid": 100},
    100:  {"lat": 30.61, "power": 24081,"w_node": 240.8, "time": 0.220, "fid": 100},
    200:  {"lat": 31.00, "power": 43465,"w_node": 217.3, "time": 0.450, "fid": 100},
    500:  {"lat": 31.24, "power": 96543,"w_node": 193.1, "time": 1.610, "fid": 100},
    1000: {"lat": 31.32, "power":180809,"w_node": 180.8, "time": 5.200, "fid": 100},
    2000: {"lat": 31.36, "power":351768,"w_node": 175.9, "time":17.970, "fid": 100},
    5000: {"lat": 31.38, "power":867088,"w_node": 173.4, "time":157.0,  "fid": 100},
}

print("\nScalability paper vs CSV comparison:")
for _, row in sc.iterrows():
    n = int(row["node_count"])
    if n in paper_scale:
        ps = paper_scale[n]
        csv_lat = row["avg_latency_ms"]
        csv_pow = row["avg_power_w"]
        csv_wn = csv_pow / n
        csv_t = row["time_per_step_s"]
        csv_fid = row["avg_fidelity_pct"]
        lat_ok = abs(csv_lat - ps["lat"]) < 0.1
        pow_ok = abs(csv_pow - ps["power"]) < 2
        wn_ok = abs(csv_wn - ps["w_node"]) < 1
        t_ok = abs(csv_t - ps["time"]) < 0.01
        fid_ok = csv_fid == ps["fid"]
        status = "OK" if all([lat_ok, pow_ok, wn_ok, t_ok, fid_ok]) else "MISMATCH"
        if status == "MISMATCH":
            print(f"  {status} N={n}: lat={csv_lat:.2f}(paper {ps['lat']}), pow={csv_pow:.0f}(paper {ps['power']}), w/n={csv_wn:.1f}(paper {ps['w_node']}), t={csv_t:.3f}(paper {ps['time']}), fid={csv_fid}(paper {ps['fid']})")
        else:
            print(f"  {status} N={n}")

# --- 5. Compute log-log slope ---
import numpy as np
nodes = sc["node_count"].values.astype(float)
power = sc["avg_power_w"].values.astype(float)
time_per = sc["time_per_step_s"].values.astype(float)
log_n = np.log10(nodes)
log_p = np.log10(power)
log_t = np.log10(time_per)
power_slope = np.polyfit(log_n, log_p, 1)[0]
time_slope = np.polyfit(log_n, log_t, 1)[0]
print(f"\nPower log-log slope: {power_slope:.3f} (paper claims 0.854)")
print(f"Time log-log slope: {time_slope:.3f} (paper claims 1.134)")

# --- 6. Normalized reward check ---
print("\n" + "="*80)
print("SECTION 5: NORMALIZED REWARD VERIFICATION")
print("="*80)
rewards = {n: computed[n]["reward"] for n in computed}
min_r = min(rewards.values())
max_r = max(rewards.values())
print(f"Raw rewards: {rewards}")
print(f"Min={min_r:.4f}, Max={max_r:.4f}")
for n in rewards:
    norm = (rewards[n] - min_r) / (max_r - min_r) if max_r != min_r else 0
    paper_norm = paper_values[n]["norm_reward"]
    match = "OK" if abs(norm - paper_norm) < 0.01 else "MISMATCH"
    print(f"  {match} {n:20s}: computed_norm={norm:.3f}, paper_norm={paper_norm:.3f}")

# --- 7. Ratio checks from paper ---
print("\n" + "="*80)
print("SECTION 6: RATIO CLAIM VERIFICATION")
print("="*80)
if "FedSemGNN" in computed and "FlatFedPPO" in computed:
    lat_ratio = computed["FlatFedPPO"]["latency"] / computed["FedSemGNN"]["latency"]
    print(f"  FlatFedPPO/FedSemGNN latency ratio: {lat_ratio:.1f}x (paper claims 3x)")
    pow_ratio = computed["FlatFedPPO"]["power"] / computed["FedSemGNN"]["power"]
    print(f"  FlatFedPPO/FedSemGNN power ratio: {pow_ratio:.1f}x (paper claims 1.4x)")
    byte_ratio = computed["FlatFedPPO"]["bytes"] / max(computed["FedSemGNN"]["bytes"], 0.001)
    print(f"  FlatFedPPO/FedSemGNN bytes ratio: {byte_ratio:.0f}x (paper claims 21x)")
if "FedSemGNN" in computed and "HierFedPPO" in computed:
    hier_byte_ratio = computed["HierFedPPO"]["bytes"] / max(computed["FedSemGNN"]["bytes"], 0.001)
    print(f"  HierFedPPO/FedSemGNN bytes ratio: {hier_byte_ratio:.0f}x (paper claims 289x)")
if "FedSemGNN" in computed and "CentralizedPPO" in computed:
    cppo_lat_ratio = computed["CentralizedPPO"]["latency"] / computed["FedSemGNN"]["latency"]
    print(f"  CentralizedPPO/FedSemGNN latency ratio: {cppo_lat_ratio:.1f}x (paper claims 3.1x)")

# --- 8. Priority data ---
print("\n" + "="*80)
print("SECTION 7: PRIORITY DATA")
print("="*80)
prio_files = ["_prio_hash20_slope02.csv", "_prio_off.csv"]
for fn in prio_files:
    fp = os.path.join(results, fn)
    if os.path.exists(fp):
        df = pd.read_csv(fp)
        print(f"\n{fn}:")
        print(f"  Rows: {len(df)}")
        for c in df.columns:
            if df[c].dtype in [float, int] and "Coord" not in c:
                print(f"    {c}: mean={df[c].mean():.4f}, last={df[c].iloc[-1]:.4f}")

# --- 9. Sensitivity data ---
print("\n" + "="*80)
print("SECTION 8: SENSITIVITY DATA")
print("="*80)
sens_dirs = ["_sens_rev1", "_sens_rev1_5t", "_sens_rev1_t5", "_sens_rev2_5t", "_sens_smoke"]
for d in sens_dirs:
    dp = os.path.join(results, d)
    if os.path.exists(dp):
        files = os.listdir(dp)
        print(f"\n{d}/: {files}")
        for f in files[:5]:
            if f.endswith('.csv'):
                df2 = pd.read_csv(os.path.join(dp, f))
                avg_lat = df2["Latency_ms"].mean() if "Latency_ms" in df2.columns else "N/A"
                avg_fid = df2["Fidelity_pct"].mean() if "Fidelity_pct" in df2.columns else "N/A"
                print(f"    {f}: rows={len(df2)}, avg_lat={avg_lat}, avg_fid={avg_fid}")
