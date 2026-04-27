import json

INPUT = "d:\\FedSemGNN\\WORKINGMODE\\FedSemGNN\\workloads\\extreme_scale_10000.json"
OUTPUT = "d:\\FedSemGNN\\WORKINGMODE\\FedSemGNN\\workloads\\extreme_scale_10000_repaired.json"

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

users = data.get("User", [])
for user in users:
    # Ensure relationships exists
    if "relationships" not in user:
        user["relationships"] = {}
    # Set mobility_model to StaticMobilityModel
    user["relationships"]["mobility_model"] = "StaticMobilityModel"

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Repaired user mobility_model for {len(users)} users. Output: {OUTPUT}")
