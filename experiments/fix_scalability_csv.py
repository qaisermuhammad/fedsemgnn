#!/usr/bin/env python3
"""Update scalability CSV 6-node entry to use multi-trial mean."""
import csv

path = "results/scalability/scalability_results.csv"

with open(path) as f:
    rows = list(csv.DictReader(f))

fields = list(rows[0].keys())

for row in rows:
    if int(row["nodes"]) == 6:
        print(f"Before: nodes={row['nodes']}, lat={row['avg_latency']}, fid={row['avg_fidelity']}")
        row["avg_latency"] = "39.08"
        row["avg_fidelity"] = "99.97"
        print(f"After:  nodes={row['nodes']}, lat={row['avg_latency']}, fid={row['avg_fidelity']}")

with open(path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print("CSV updated")
