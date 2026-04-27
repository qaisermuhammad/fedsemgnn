import json
import os

DATASET_PATH = os.path.join('workloads', 'extreme_scale_dataset_1000_complete.json')

def fix_attributes(obj):
    if isinstance(obj, dict):
        # Only add 'attributes' if 'relationships' exists and 'attributes' is missing
        if 'relationships' in obj and 'attributes' not in obj:
            obj['attributes'] = {}
        for v in obj.values():
            fix_attributes(v)
    elif isinstance(obj, list):
        for v in obj:
            fix_attributes(v)

if __name__ == "__main__":
    with open(DATASET_PATH, 'r') as f:
        data = json.load(f)
    fix_attributes(data)
    with open(DATASET_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Repaired missing 'attributes' keys in {DATASET_PATH}")
