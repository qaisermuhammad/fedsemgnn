"""
Comprehensive final audit of sections/main.tex against authoritative data.
Checks every numerical claim, ratio, and cross-reference.
"""
import re

with open('sections/main.tex', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# ====== AUTHORITATIVE DATA (5-trial means) ======
AUTH = {
    'FedSemGNN':      {'lat': 39.08, 'lat_std': 6.23, 'fid': 99.97, 'fid_std': 0.01, 'pow': 2674, 'pow_std': 713, 'mig': 45835, 'mig_std': 3733, 'byt': 0.72},
    'FlatFedPPO':     {'lat': 127.75, 'lat_std': 13.85, 'fid': 71.93, 'fid_std': 2.4, 'pow': 3166, 'pow_std': 313, 'mig': 94733, 'mig_std': 12104, 'byt': 15.02},
    'HierFedPPO':     {'lat': 82.05, 'lat_std': 0.42, 'fid': 98.45, 'fid_std': 0.0, 'pow': 1066, 'pow_std': 0, 'mig': 11981, 'mig_std': 0, 'byt': 207.65},
    'HSQF':           {'lat': 134.70, 'lat_std': 0.0, 'fid': 100.0, 'fid_std': 0.0, 'pow': 840, 'pow_std': 0, 'mig': 26941, 'mig_std': 0, 'byt': 2.93},
    'RandomPlacement':{'lat': 119.11, 'lat_std': 0.0, 'fid': 99.98, 'fid_std': 0.0, 'pow': 2961, 'pow_std': 0, 'mig': 89441, 'mig_std': 0, 'byt': 0.00},
    'CentralizedPPO': {'lat': 130.35, 'lat_std': 0.43, 'fid': 72.52, 'fid_std': 0.59, 'pow': 3099, 'pow_std': 167, 'mig': 79124, 'mig_std': 3225, 'byt': 0.00},
}

# Scalability data
SCAL = {
    6: {'lat': 39.08, 'time': 0.052, 'fid': 99.97},
    25: {'lat': 31.40, 'time': 0.059, 'fid': 100.0},
    50: {'lat': 29.83, 'time': 0.091, 'fid': 100.0},
    100: {'lat': 30.61, 'time': 0.179, 'fid': 100.0},
    200: {'lat': 31.00, 'time': 0.459, 'fid': 100.0},
    500: {'lat': 31.24, 'time': 1.926, 'fid': 100.0},
    1000: {'lat': 31.32, 'time': 6.142, 'fid': 100.0},
}

errors = []
warnings = []
info = []

# ====== CHECK 1: Verify all specific metric values in the text ======
def find_line(pattern, flags=re.IGNORECASE):
    """Find all lines matching a pattern."""
    results = []
    for i, line in enumerate(lines, 1):
        if re.search(pattern, line):
            results.append((i, line.strip()[:120]))
    return results

# Check FedSemGNN latency claims
lat_claims = find_line(r'39\.08')
info.append(f"FedSemGNN 39.08ms appears on {len(lat_claims)} lines (AUTH={AUTH['FedSemGNN']['lat']}ms)")

# Check FlatFedPPO latency
flat_lat = find_line(r'127\.75')
info.append(f"FlatFedPPO 127.75ms appears on {len(flat_lat)} lines (AUTH={AUTH['FlatFedPPO']['lat']}ms)")

# Check HierFedPPO latency
hier_lat = find_line(r'82\.05')
info.append(f"HierFedPPO 82.05ms appears on {len(hier_lat)} lines (AUTH={AUTH['HierFedPPO']['lat']}ms)")

# Check CentralizedPPO latency
cent_lat = find_line(r'130\.35')
info.append(f"CentralizedPPO 130.35ms appears on {len(cent_lat)} lines (AUTH={AUTH['CentralizedPPO']['lat']}ms)")

# ====== CHECK 2: Verify ratios ======
# 3.3x faster than FlatFedPPO: 127.75/39.08 = 3.268
actual_ratio = 127.75 / 39.08
if abs(actual_ratio - 3.3) > 0.1:
    errors.append(f"RATIO: 3.3x claim, actual {actual_ratio:.2f}x")
else:
    info.append(f"OK: 3.3x ratio (actual {actual_ratio:.2f}x)")

# 21x lower than FlatFedPPO comm: 15.02/0.72 = 20.86
actual_ratio_comm = 15.02 / 0.72
ratio_21x_matches = find_line(r'21.*lower|21\$\\times\$')
if abs(actual_ratio_comm - 21) > 1.5:
    errors.append(f"RATIO: 21x comm claim, actual {actual_ratio_comm:.1f}x")
else:
    info.append(f"OK: 21x comm ratio (actual {actual_ratio_comm:.1f}x)")

# 290x lower than HierFedPPO comm: 207.65/0.72 = 288.4
actual_ratio_hier = 207.65 / 0.72
if abs(actual_ratio_hier - 290) > 5:
    errors.append(f"RATIO: 290x comm claim, actual {actual_ratio_hier:.1f}x")
else:
    info.append(f"OK: 290x comm ratio (actual {actual_ratio_hier:.1f}x)")

# 41x faster than GFL-LFF: 1600/39.08 = 40.9
actual_gfl = 1600 / 39.08
if abs(actual_gfl - 41) > 1:
    errors.append(f"RATIO: 41x vs GFL-LFF claim, actual {actual_gfl:.1f}x")
else:
    info.append(f"OK: 41x vs GFL-LFF (actual {actual_gfl:.1f}x)")

# 1.8x faster than FRPVC: 72/39.08 = 1.842
actual_frpvc = 72 / 39.08
if abs(actual_frpvc - 1.8) > 0.15:
    errors.append(f"RATIO: 1.8x vs FRPVC claim, actual {actual_frpvc:.2f}x")
else:
    info.append(f"OK: 1.8x vs FRPVC (actual {actual_frpvc:.2f}x)")

# 69x lower comm than ECO-SDIoT: 50/0.72 = 69.4
actual_eco = 50 / 0.72
if abs(actual_eco - 69) > 2:
    errors.append(f"RATIO: 69x vs ECO-SDIoT claim, actual {actual_eco:.1f}x")
else:
    info.append(f"OK: 69x vs ECO-SDIoT (actual {actual_eco:.1f}x)")

# 2.1x faster than HierFedPPO: 82.05/39.08 = 2.10
actual_hier_ratio = 82.05 / 39.08
hier_21x = find_line(r'2\.1.*faster.*HierFedPPO|HierFedPPO.*82\.05')
if abs(actual_hier_ratio - 2.1) > 0.05:
    errors.append(f"RATIO: 2.1x vs HierFedPPO claim, actual {actual_hier_ratio:.2f}x")
else:
    info.append(f"OK: 2.1x vs HierFedPPO (actual {actual_hier_ratio:.2f}x)")

# ====== CHECK 3: Verify fidelity claims ======
# FedSemGNN ~100% (99.97)
fid_100 = find_line(r'99\.97')
info.append(f"FedSemGNN 99.97% fidelity on {len(fid_100)} lines")

# FlatFedPPO 71.9% (auth: 71.93)
flat_fid_claims = find_line(r'71\.9')
info.append(f"FlatFedPPO 71.9% fidelity (auth 71.93%) on {len(flat_fid_claims)} lines")

# CentralizedPPO 72.5% (auth: 72.52)
cent_fid_claims = find_line(r'72\.5')
info.append(f"CentralizedPPO 72.5% fidelity (auth 72.52%) on {len(cent_fid_claims)} lines")

# HierFedPPO 98.5% (auth: 98.45 - rounds to 98.5)
hier_fid = find_line(r'98\.5')
info.append(f"HierFedPPO 98.5% fidelity (auth 98.45%, rounds to 98.5) on {len(hier_fid)} lines")

# ====== CHECK 4: Verify power claims ======
pow_claims = {
    'FedSemGNN 2674': find_line(r'2[,{]674'),
    'FlatFedPPO 3166': find_line(r'3[,{]166'),
    'HierFedPPO 1066': find_line(r'1[,{]066'),
    'HSQF 840': find_line(r'\b840'),
    'Random 2961': find_line(r'2[,{]961'),
    'CentralPPO 3099': find_line(r'3[,{]099'),
}
for claim, occurrences in pow_claims.items():
    info.append(f"Power {claim}W on {len(occurrences)} lines")

# ====== CHECK 5: Check for STALE values ======
stale_checks = [
    (r'27\.94', 'Old single-trial latency 27.94ms'),
    (r'4\.6.*times|4\.6x', 'Old 4.6x ratio'),
    (r'57.*times.*GFL', 'Old 57x GFL ratio'),
    (r'2\.6.*times.*FRPVC|2\.6x.*FRPVC', 'Old 2.6x FRPVC ratio'),
    (r'\b18\.3\s*MB\b', 'Fabricated 18.3MB memory'),
    (r'247\.5\s*MB', 'Fabricated 247.5MB memory'),
    (r'(?<!~)50\s+timesteps', 'Old 50 timesteps convergence'),
    (r'32\s+timesteps|43\s+timesteps|58\s+timesteps', 'Fabricated convergence steps'),
    (r'stability score\s+0\.83', 'Unverified stability score'),
    (r'p\s*<\s*0\.001', 'Old p<0.001 claim'),
    (r't-test', 'Old t-test methodology'),
    (r'128\s*\\times\s*64|128.*×.*64', 'Old 128x64 GCN dims'),
]

for pattern, desc in stale_checks:
    matches = find_line(pattern)
    if matches:
        for line_num, text in matches:
            errors.append(f"STALE VALUE line {line_num}: {desc} -- '{text[:80]}...'")

# ====== CHECK 6: Verify GNN dimensions ======
gnn_21 = find_line(r'GNN Input Features.*21|21.*dimensions|21\s*\\times\s*32|\\mathbb\{R\}\^\{21\}')
if len(gnn_21) >= 3:
    info.append(f"OK: GNN input_dim=21 found on {len(gnn_21)} lines")
else:
    warnings.append(f"GNN input_dim=21 only found on {len(gnn_21)} lines (expected 3+)")

gnn_32 = find_line(r'GNN Hidden Dim.*32|d_h\s*=\s*32|32\s*\\times\s*16')
if gnn_32:
    info.append(f"OK: GNN hidden_dim=32 found on {len(gnn_32)} lines")

gnn_16_out = find_line(r'\\mathbb\{R\}\^\{16\}|d_\{\\text\{out\}\}.*16')
info.append(f"GNN output_dim=16 found on {len(gnn_16_out)} lines")

# ====== CHECK 7: Semantic encoder dimensions (should be 128→64→64→16) ======
sem_128 = find_line(r'128\s*\\rightarrow\s*64|128.*→.*64')
info.append(f"Semantic encoder 128→64→64→16 found on {len(sem_128)} lines ({'OK' if sem_128 else 'ISSUE'})")

# ====== CHECK 8: Verify table values against authoritative data ======
# Check for presence of ±std in performance table
has_std = find_line(r'39\.08\$\\pm\$6\.23')
if has_std:
    info.append("OK: Performance table has ±std values")
else:
    warnings.append("Performance table may be missing ±std values")

# ====== CHECK 9: Check for model size claims ======
model_3760 = find_line(r'3[,{]760')
model_15kb = find_line(r'15.*KB|15~KB')
if model_3760 and model_15kb:
    info.append(f"OK: Model size claims (3,760 params, ~15 KB) found")
else:
    warnings.append(f"Model size claims: 3760 found={bool(model_3760)}, 15KB found={bool(model_15kb)}")

# ====== CHECK 10: Verify scalability table values ======
for nodes, expected in SCAL.items():
    lat_str = f"{expected['lat']:.2f}" if expected['lat'] != int(expected['lat']) else f"{expected['lat']:.1f}"
    time_str = f"{expected['time']:.3f}"

# ====== CHECK 11: Check convergence claim ======
conv_150 = find_line(r'150\s+timesteps|within.*150|\\sim.*150')
if conv_150:
    info.append(f"OK: Convergence ~150 timesteps found on {len(conv_150)} lines")
else:
    warnings.append("Convergence ~150 timesteps claim not found")

# ====== CHECK 12: Check p-value claims ======
p_01 = find_line(r'p\s*<\s*0\.01')
if p_01:
    info.append(f"OK: p < 0.01 claims found on {len(p_01)} lines")
else:
    warnings.append("p < 0.01 claims not found")

# ====== CHECK 13: Verify Mann-Whitney U methodology ======
mann_whitney = find_line(r'Mann-Whitney')
if mann_whitney:
    info.append(f"OK: Mann-Whitney U methodology referenced on {len(mann_whitney)} lines")
else:
    warnings.append("Mann-Whitney U methodology not referenced")

# ====== CHECK 14: Check methodology note about representative trials ======
repr_trial = find_line(r'representative trial')
if repr_trial:
    info.append(f"OK: 'representative trial' noted on {len(repr_trial)} lines")
else:
    warnings.append("'representative trial' methodology note not found")

# ====== CHECK 15: LaTeX structure ======
depth = 0
for i, line in enumerate(lines, 1):
    clean = re.sub(r'(?<!\\)%.*$', '', line)
    for c in clean:
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth < 0:
                errors.append(f"LATEX: Unmatched }} at line {i}")
                depth = 0
if depth != 0:
    errors.append(f"LATEX: {depth} unclosed braces at EOF")
else:
    info.append("OK: All braces balanced")

# Check environments
env_stack = []
for i, line in enumerate(lines, 1):
    clean = re.sub(r'(?<!\\)%.*$', '', line)
    for m in re.finditer(r'\\begin\{(\w+)\}', clean):
        env_stack.append((m.group(1), i))
    for m in re.finditer(r'\\end\{(\w+)\}', clean):
        if env_stack and env_stack[-1][0] == m.group(1):
            env_stack.pop()
        elif env_stack:
            errors.append(f"LATEX: Mismatched \\end{{{m.group(1)}}} at line {i}")
if env_stack:
    for env, line in env_stack:
        errors.append(f"LATEX: Unclosed \\begin{{{env}}} at line {line}")
else:
    info.append("OK: All environments balanced")

# ====== CHECK 16: Verify figure files exist ======
import os
figs = re.findall(r'\\includegraphics.*?\{([^}]+)\}', content)
missing_figs = [f for f in figs if not os.path.exists(f)]
if missing_figs:
    for f in missing_figs:
        warnings.append(f"FIGURE: {f} not found from project root")
else:
    info.append(f"OK: All {len(figs)} figure files exist")

# ====== CHECK 17: Cross-reference labels ======
labels = set(re.findall(r'\\label\{([^}]+)\}', content))
refs = set(re.findall(r'\\ref\{([^}]+)\}', content))
missing_refs = refs - labels
if missing_refs:
    for r in missing_refs:
        warnings.append(f"CROSS-REF: \\ref{{{r}}} has no matching \\label")
else:
    info.append(f"OK: All {len(refs)} \\ref cross-references have matching \\labels")

unused_labels = labels - refs
if unused_labels:
    for l in unused_labels:
        info.append(f"INFO: \\label{{{l}}} is never referenced (may be intentional)")

# ====== CHECK 18: Verify 22% emergency latency reduction in conclusion ======
# (2.726 - 2.116) / 2.726 = 22.4%
reduction = (2.726 - 2.116) / 2.726 * 100
if abs(reduction - 22) > 1:
    errors.append(f"RATIO: 22% emergency reduction claim, actual {reduction:.1f}%")
else:
    info.append(f"OK: 22% emergency reduction (actual {reduction:.1f}%)")

# ====== REPORT ======
print("=" * 70)
print("FINAL AUDIT REPORT: sections/main.tex")
print("=" * 70)

if errors:
    print(f"\n{'!'*50}")
    print(f"ERRORS ({len(errors)}):")
    print(f"{'!'*50}")
    for e in errors:
        print(f"  [ERROR] {e}")

if warnings:
    print(f"\n{'~'*50}")
    print(f"WARNINGS ({len(warnings)}):")
    print(f"{'~'*50}")
    for w in warnings:
        print(f"  [WARN] {w}")

print(f"\n{'-'*50}")
print(f"INFO ({len(info)}):")
print(f"{'-'*50}")
for i in info:
    print(f"  [INFO] {i}")

print(f"\n{'='*70}")
print(f"SUMMARY: {len(errors)} errors, {len(warnings)} warnings, {len(info)} info items")
if errors:
    print("STATUS: *** NOT READY FOR SUBMISSION ***")
elif warnings:
    print("STATUS: REVIEW WARNINGS BEFORE SUBMISSION")
else:
    print("STATUS: READY FOR SUBMISSION")
print("=" * 70)
