#!/usr/bin/env python3
import json, copy, sys
from typing import Dict, Any, List, Tuple

SRC = "sample_dataset3.json"
DST = "scale_1000_nodes.json"
FACTOR = 167

# Top-level entity keys we expect (order doesn't matter)
ENTITY_KEYS = [
    "NetworkSwitch",
    "NetworkLink",
    "BaseStation",
    "User",
    "ContainerLayer",
    "ContainerImage",
    "Service",
    "ContainerRegistry",
    "Application",
    "EdgeServer",
    "RandomDurationAndIntervalAccessPattern",
    "CircularDurationAndIntervalAccessPattern",
]

# Relationship fields that are single refs or lists of refs of the form {"class": X, "id": Y}
REL_KEYS = {
    # generic relationship names we saw in sample
    "power_model",           # string in sample (no remap)
    "edge_servers",
    "links",
    "base_station",
    "network_switch",
    "users",
    "applications",
    "active_flows",
    "nodes",
    "topology",              # refers to external Topology; we will leave as-is unless present in mapping
    "server",
    "services",
    "container_layers",
    "container_images",
    "container_registries",
    "app",
    "user",
    "application",
}

def is_ref(obj: Any) -> bool:
    """Detect {"class": <Type>, "id": <int>} reference."""
    return isinstance(obj, dict) and set(obj.keys()) == {"class", "id"} and isinstance(obj["id"], int) and isinstance(obj["class"], str)

def remap_ref(obj: Dict[str, Any], replica_idx: int, id_map: Dict[Tuple[str,int,int], int]) -> Dict[str, Any]:
    """Return a new ref with remapped id for this replica if we know the mapping; else return as-is."""
    cls = obj["class"]
    old_id = obj["id"]
    key = (cls, old_id, replica_idx)
    if key in id_map:
        return {"class": cls, "id": id_map[key]}
    # Not all refs exist as real entities (e.g., Topology); keep original
    return obj

def deep_remap_relationships(item: Dict[str, Any], replica_idx: int, id_map: Dict[Tuple[str,int,int], int]) -> None:
    """Walk the 'relationships' dict and remap any {"class","id"} references (single or lists)."""
    rels = item.get("relationships")
    if not isinstance(rels, dict):
        return

    for k, v in list(rels.items()):
        if k not in REL_KEYS:
            continue
        # single ref
        if is_ref(v):
            rels[k] = remap_ref(v, replica_idx, id_map)
        # list of refs
        elif isinstance(v, list):
            new_list = []
            for elem in v:
                if is_ref(elem):
                    new_list.append(remap_ref(elem, replica_idx, id_map))
                else:
                    new_list.append(elem)  # leave non-refs as-is
            rels[k] = new_list
        # dict-of-refs (rare but appears e.g., "access_patterns": {"1": {...}})
        elif isinstance(v, dict):
            new_dict = {}
            for dk, dv in v.items():
                if is_ref(dv):
                    new_dict[dk] = remap_ref(dv, replica_idx, id_map)
                else:
                    new_dict[dk] = dv
            rels[k] = new_dict

def remap_user_attribute_maps(user_item: Dict[str, Any], replica_idx: int, id_map: Dict[Tuple[str,int,int], int]) -> None:
    """
    Users have extra maps with string keys pointing to IDs:
      - "delays":        { "<ApplicationID>": ... }   (null or number)
      - "delay_slas":    { "<ApplicationID>": SLA }
      - "making_requests": { "<ApplicationID>": { "<ServiceID>": bool } }
    We remap those keys into the replicated Application/Service IDs.
    """
    attrs = user_item.get("attributes", {})
    def maybe_int(s):
        try:
            return int(s)
        except:
            return None

    # delays
    if isinstance(attrs.get("delays"), dict):
        new_d = {}
        for k, v in attrs["delays"].items():
            old = maybe_int(k)
            if old is None:  # keep non-int keys
                new_d[k] = v
                continue
            app_key = ("Application", old, replica_idx)
            new_id = id_map.get(app_key, old)
            new_d[str(new_id)] = v
        attrs["delays"] = new_d

    # delay_slas
    if isinstance(attrs.get("delay_slas"), dict):
        new_d = {}
        for k, v in attrs["delay_slas"].items():
            old = maybe_int(k)
            if old is None:
                new_d[k] = v
                continue
            app_key = ("Application", old, replica_idx)
            new_id = id_map.get(app_key, old)
            new_d[str(new_id)] = v
        attrs["delay_slas"] = new_d

    # making_requests: { app_id: { service_id: bool } }
    if isinstance(attrs.get("making_requests"), dict):
        new_outer = {}
        for app_k, inner in attrs["making_requests"].items():
            app_old = maybe_int(app_k)
            app_new = id_map.get(("Application", app_old, replica_idx), app_old) if app_old is not None else app_k
            if isinstance(inner, dict):
                new_inner = {}
                for svc_k, val in inner.items():
                    svc_old = maybe_int(svc_k)
                    svc_new = id_map.get(("Service", svc_old, replica_idx), svc_old) if svc_old is not None else svc_k
                    new_inner[str(svc_new)] = val
                new_outer[str(app_new)] = new_inner
            else:
                new_outer[str(app_new)] = inner
        attrs["making_requests"] = new_outer

    user_item["attributes"] = attrs

def main():
    with open(SRC, "r") as f:
        src = json.load(f)

    # sanity: ensure keys exist; default to empty lists for missing ones
    for key in ENTITY_KEYS:
        src.setdefault(key, [])

    # Build base counts per entity type and id offset helpers
    base_counts = {k: len(src[k]) for k in ENTITY_KEYS}
    # Precompute mapping: for each type and original id, and for each replica r,
    # the new id = old_id + r * base_count[type]
    id_map: Dict[Tuple[str,int,int], int] = {}

    for etype in ENTITY_KEYS:
        n = base_counts[etype]
        if n == 0:
            continue
        for r in range(FACTOR):
            offset = r * n
            for item in src[etype]:
                old_id = item.get("attributes", {}).get("id")
                if isinstance(old_id, int):
                    id_map[(etype, old_id, r)] = old_id + offset

    # Clone each type FACTOR times, rewriting IDs and relationships within the same replica r
    out: Dict[str, List[Dict[str, Any]]] = {k: [] for k in ENTITY_KEYS}

    for etype in ENTITY_KEYS:
        items = src[etype]
        n = base_counts[etype]
        if n == 0:
            continue

        for r in range(FACTOR):
            offset = r * n
            for orig in items:
                item = copy.deepcopy(orig)

                # Remap the entity's own id
                attrs = item.get("attributes", {})
                if isinstance(attrs.get("id"), int):
                    attrs["id"] = attrs["id"] + offset
                item["attributes"] = attrs

                # Remap relationships to the SAME replica r
                deep_remap_relationships(item, r, id_map)

                # Special handling for User attribute maps (string keys that encode IDs)
                if etype == "User":
                    remap_user_attribute_maps(item, r, id_map)

                out[etype].append(item)

    # Write output
    with open(DST, "w") as f:
        json.dump(out, f, indent=2, allow_nan=True)

    total_counts = {k: len(v) for k, v in out.items()}
    print(f"Wrote {DST}")
    print("Counts x100:", json.dumps(total_counts, indent=2))

if __name__ == "__main__":
    # Allow overriding file names from CLI if desired
    if len(sys.argv) >= 2:
        SRC = sys.argv[1]
    if len(sys.argv) >= 3:
        DST = sys.argv[2]
    main()
