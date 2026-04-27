"""
Unified scalable topology generator and patch point for large-scale simulations.
Supports k-regular ring, random, and small-world topologies.
Does NOT modify or overwrite any existing dataset files.
If --use-generated-topology is set, this module will generate a topology and provide it to the simulation.

All generated entities match the exact JSON structure expected by EdgeSimPy
(same fields as workloads/sample_dataset3.json).
"""

import argparse
import random as _random
import networkx as nx
import math


def maybe_generate_topology(args, num_nodes):
    """
    If args.use_generated_topology is set, return a generated topology.
    Otherwise, return None (use dataset as usual).
    """
    if hasattr(args, 'use_generated_topology') and args.use_generated_topology:
        mode = getattr(args, 'topology_mode', 'ring')
        degree = getattr(args, 'topology_degree', 4)
        return get_topology(num_nodes, mode=mode, degree=degree)
    return None


# ---------------------------------------------------------------------------
#  Shared entity builder - produces entities matching native EdgeSimPy format
# ---------------------------------------------------------------------------

def _build_entities(G, num_nodes):
    """
    Given a networkx graph G (nodes 0..num_nodes-1), build ALL entity dicts
    that EdgeSimPy expects in its JSON dataset format.

    Returns:
        (switches, links, base_stations, edge_servers, topology,
         services, registries, images, layers, users, applications,
         access_patterns)
    """
    # --- NetworkLinks from graph edges ---
    links = []
    for link_id, (u, v) in enumerate(G.edges(), start=1):
        links.append({
            "attributes": {
                "id": link_id,
                "delay": 5,
                "bandwidth": 12.5,
                "bandwidth_demand": 0,
                "active": True,
            },
            "relationships": {
                "topology": {"class": "Topology", "id": 1},
                "active_flows": [],
                "applications": [],
                "nodes": [
                    {"class": "NetworkSwitch", "id": u + 1},
                    {"class": "NetworkSwitch", "id": v + 1},
                ],
            },
        })

    # --- Core entities: NetworkSwitch, BaseStation, EdgeServer, User ---
    switches = []
    base_stations = []
    edge_servers = []
    users = []

    # Grid coordinates for spatial layout
    grid_side = max(1, int(math.ceil(math.sqrt(num_nodes))))

    for i in range(num_nodes):
        node_id = i + 1  # 1-indexed
        ux = i % grid_side
        uy = i // grid_side

        # --- BaseStation (matches native format exactly) ---
        base_stations.append({
            "attributes": {
                "id": node_id,
                "coordinates": [ux, uy],
                "wireless_delay": 5,
            },
            "relationships": {
                "users": [{"class": "User", "id": node_id}],
                "edge_servers": [{"class": "EdgeServer", "id": node_id}],
                "network_switch": {"class": "NetworkSwitch", "id": node_id},
            },
        })

        # --- EdgeServer (matches native format exactly) ---
        edge_servers.append({
            "attributes": {
                "id": node_id,
                "available": True,
                "model_name": "E5430",
                "cpu": 8,
                "memory": 16384,
                "disk": 131072,
                "cpu_demand": 0,
                "memory_demand": 0,
                "disk_demand": 0,
                "coordinates": [ux, uy],
                "max_concurrent_layer_downloads": 3,
                "active": True,
                "power_model_parameters": {
                    "max_power_consumption": 265,
                    "static_power_percentage": 0.6264,
                },
            },
            "relationships": {
                "power_model": "LinearServerPowerModel",
                "base_station": {"class": "BaseStation", "id": node_id},
                "network_switch": {"class": "NetworkSwitch", "id": node_id},
                "services": [],
                "container_layers": [],
                "container_images": [],
                "container_registries": [],
            },
        })

        # --- User (matches native format - one per BaseStation) ---
        app_id_str = str(node_id)
        users.append({
            "attributes": {
                "id": node_id,
                "coordinates": [ux, uy],
                # Short trace - EdgeSimPy expects at least one entry
                "coordinates_trace": [[ux, uy]],
                # These are attributes in native format, not relationships
                "delays": {app_id_str: None},
                "delay_slas": {app_id_str: 45},
                "communication_paths": {},
                "making_requests": {app_id_str: {"1": True}},
            },
            "relationships": {
                "base_station": {"class": "BaseStation", "id": node_id},
                # access_patterns is a dict keyed by app_id string, not a list
                "access_patterns": {
                    app_id_str: {"class": "CircularDurationAndIntervalAccessPattern", "id": node_id}
                },
                "mobility_model": "pathway",
                "applications": [{"class": "Application", "id": node_id}],
            },
        })

        # --- NetworkSwitch ---
        switches.append({
            "attributes": {
                "id": node_id,
                "coordinates": [ux, uy],
                "active": True,
                "power_model_parameters": {
                    "chassis_power": 60,
                    "ports_power_consumption": {"125": 1, "12.5": 0.3},
                },
            },
            "relationships": {
                "power_model": "ConteratoNetworkPowerModel",
                "edge_servers": [{"class": "EdgeServer", "id": node_id}],
                "links": [],
                "base_station": {"class": "BaseStation", "id": node_id},
            },
        })

    # --- Topology singleton ---
    topology = [{"attributes": {"id": 1, "active": True}, "relationships": {}}]

    # --- ContainerLayers ---
    num_layers = min(30, max(10, num_nodes // 10))
    layers = []
    for i in range(num_layers):
        layers.append({
            "attributes": {
                "digest": f"sha256:layer{i + 1:04d}",
                "size": 2 + (i % 10),
                "instruction": f"RUN step{i + 1}",
            },
            "relationships": {
                "server": {"class": "EdgeServer", "id": (i % num_nodes) + 1},
            },
        })

    # --- ContainerImages ---
    num_images = min(12, max(6, num_nodes // 10))
    images = []
    for i in range(num_images):
        layer_digests = [layers[i % num_layers]["attributes"]["digest"]]
        if i % 2 == 0 and num_layers > 1:
            layer_digests.append(layers[(i + 1) % num_layers]["attributes"]["digest"])
        images.append({
            "attributes": {
                "id": i + 1,
                "name": f"img_{i + 1}",
                "tag": "latest",
                "digest": f"sha256:img{i + 1:04d}",
                "layers_digests": layer_digests,
                "architecture": "amd64",
            },
            "relationships": {
                "server": {"class": "EdgeServer", "id": (i % num_nodes) + 1},
            },
        })

    # --- Services (matches native format) ---
    num_services = max(6, num_nodes // 5)
    services = []
    for i in range(num_services):
        svc_id = i + 1
        img = images[i % num_images]
        services.append({
            "attributes": {
                "id": svc_id,
                "label": f"svc_{svc_id}",
                "state": 0,
                "_available": True,
                "cpu_demand": 1 + (i % 3),
                "memory_demand": 64 + (i % 3) * 32,
                "image_digest": img["attributes"]["digest"],
            },
            "relationships": {
                "application": {"class": "Application", "id": (i % num_nodes) + 1},
                "server": None,
            },
        })

    # --- ContainerRegistries (one per edge server, matching native) ---
    registries = []
    for i in range(num_nodes):
        registries.append({
            "attributes": {
                "id": i + 1,
                "cpu_demand": 1,
                "memory_demand": 1024,
            },
            "relationships": {
                "server": {"class": "EdgeServer", "id": i + 1},
            },
        })

    # Patch EdgeServer relationships to reference their registry
    for i, es in enumerate(edge_servers):
        reg_ref = {"class": "ContainerRegistry", "id": i + 1}
        es["relationships"]["container_registries"] = [reg_ref]

    # --- Applications (one per user, matching native) ---
    applications = []
    for i in range(num_nodes):
        app_id = i + 1
        # Each application owns the services whose app reference points here
        app_svc_refs = [
            {"class": "Service", "id": s["attributes"]["id"]}
            for s in services
            if s["relationships"]["application"]["id"] == app_id
        ]
        applications.append({
            "attributes": {
                "id": app_id,
                "label": "",
            },
            "relationships": {
                "services": app_svc_refs,
                "users": [{"class": "User", "id": app_id}],
            },
        })

    # --- CircularDurationAndIntervalAccessPattern (one per user) ---
    access_patterns = []
    for i in range(num_nodes):
        access_patterns.append({
            "attributes": {
                "id": i + 1,
                "duration_values": [float("inf")],
                "interval_values": [0],
                "history": [
                    {
                        "start": 1,
                        "end": float("inf"),
                        "duration": float("inf"),
                        "waiting_time": 0,
                        "access_time": 0,
                        "interval": 0,
                        "next_access": float("inf"),
                    }
                ],
            },
            "relationships": {
                "user": {"class": "User", "id": i + 1},
                "app": {"class": "Application", "id": i + 1},
            },
        })

    return (
        switches,
        links,
        base_stations,
        edge_servers,
        topology,
        services,
        registries,
        images,
        layers,
        users,
        applications,
        access_patterns,
    )


# ---------------------------------------------------------------------------
#  Graph generators (only produce the networkx graph; entities built by helper)
# ---------------------------------------------------------------------------

def generate_k_regular_ring(num_nodes, degree=4):
    """Generate a k-regular ring topology."""
    degree = min(degree, num_nodes - 1)
    if degree % 2 != 0:
        degree -= 1
    degree = max(2, degree)
    G = nx.random_regular_graph(degree, num_nodes, seed=42)
    return _build_entities(G, num_nodes)


def generate_random_topology(num_nodes, avg_degree=4):
    """Generate a random topology (Erdos-Renyi)."""
    p = avg_degree / max(1, num_nodes - 1)
    G = nx.erdos_renyi_graph(num_nodes, p, seed=42)
    # Ensure connected
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        for idx in range(1, len(components)):
            u = next(iter(components[idx - 1]))
            v = next(iter(components[idx]))
            G.add_edge(u, v)
    return _build_entities(G, num_nodes)


def generate_small_world(num_nodes, k=4, p=0.1):
    """Generate a Watts-Strogatz small-world topology."""
    k = min(k, num_nodes - 1)
    if k % 2 != 0:
        k -= 1
    k = max(2, k)
    G = nx.watts_strogatz_graph(num_nodes, k, p, seed=42)
    return _build_entities(G, num_nodes)


# ---------------------------------------------------------------------------
#  Dispatcher
# ---------------------------------------------------------------------------

def get_topology(num_nodes, mode="ring", **kwargs):
    degree = kwargs.get("degree", 4)
    if mode == "ring":
        return generate_k_regular_ring(num_nodes, degree)
    elif mode == "random":
        return generate_random_topology(num_nodes, avg_degree=degree)
    elif mode == "smallworld":
        return generate_small_world(num_nodes, k=degree)
    else:
        raise ValueError(f"Unknown topology mode: {mode}")
