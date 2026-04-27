#!/usr/bin/env python3
"""Compute all derived ratios from multi-trial means."""

# 5-trial means
fed = {"lat": 39.08, "fid": 99.97, "pow": 2673.6, "mig": 45835, "bytes": 0.7172}
flat = {"lat": 127.75, "fid": 71.93, "pow": 3166.1, "mig": 94733, "bytes": 15.0162}
hier = {"lat": 82.05, "fid": 98.45, "pow": 1065.7, "mig": 11981, "bytes": 207.6530}
hsqf = {"lat": 134.70, "fid": 100.0, "pow": 840.3, "mig": 26941, "bytes": 2.9297}
rand = {"lat": 119.11, "fid": 99.98, "pow": 2961.3, "mig": 89441, "bytes": 0.0019}
cent = {"lat": 130.35, "fid": 72.52, "pow": 3099.0, "mig": 79124, "bytes": 0.0}

print("=== BASELINE RATIOS ===")
print(f"FedSemGNN vs FlatFedPPO latency: {flat['lat']/fed['lat']:.1f}x")
print(f"FedSemGNN vs CentralizedPPO lat: {cent['lat']/fed['lat']:.1f}x")
print(f"FedSemGNN vs HierFedPPO lat: {hier['lat']/fed['lat']:.1f}x")
print(f"FedSemGNN vs HSQF lat: {hsqf['lat']/fed['lat']:.1f}x")
print(f"FedSemGNN vs FlatFedPPO comm: {flat['bytes']/fed['bytes']:.0f}x")
print(f"FedSemGNN vs HierFedPPO comm: {hier['bytes']/fed['bytes']:.0f}x")
print(f"FedSemGNN vs FlatFedPPO power: {flat['pow']/fed['pow']:.2f}x")
print(f"FedSemGNN vs CentralPPO power: {cent['pow']/fed['pow']:.2f}x")

print("\n=== SOTA COMPARISON ===")
print(f"vs GFL-LFF (1600ms): {1600/fed['lat']:.0f}x")
print(f"vs FRPVC (72ms): {72/fed['lat']:.1f}x")
print(f"vs ECO-SDIoT comm (50MB): {50/fed['bytes']:.0f}x")
print(f"vs FRPVC comm (5MB): {5/fed['bytes']:.0f}x")
