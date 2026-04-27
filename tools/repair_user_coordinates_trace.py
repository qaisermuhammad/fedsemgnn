import json

INPUT = "d:\\FedSemGNN\\WORKINGMODE\\FedSemGNN\\workloads\\extreme_scale_10000_repaired.json"
OUTPUT = "d:\\FedSemGNN\\WORKINGMODE\\FedSemGNN\\workloads\\extreme_scale_10000_final.json"
SIM_STEPS = 1000  # You can adjust this to match your simulation steps

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

users = data.get("User", [])
for user in users:
    attrs = user.get("attributes", {})
    coord = attrs.get("coordinates", [0, 0])
    trace = attrs.get("coordinates_trace", [coord])
    # Extend or repeat the trace to SIM_STEPS
    if len(trace) < SIM_STEPS:
        trace = trace + [coord] * (SIM_STEPS - len(trace))
    attrs["coordinates_trace"] = trace[:SIM_STEPS]
    user["attributes"] = attrs

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Repaired coordinates_trace for {len(users)} users. Output: {OUTPUT}")
