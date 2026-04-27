"""
High-resolution diagram generator for FedSemGNN.

This script creates a comprehensive set of system diagrams and exports each
as both PNG (500 DPI) and PDF (vector). All outputs are written to this
directory only.

Diagrams produced:
1) Architecture overview
2) Federated learning cycle
3) Data flow (request to decision)
4) Sequence of a single placement
5) Deployment/topology (flat vs hierarchical)
6) Activity/state lifecycles
7) Component/module map
8) Timing/latency timeline
9) Communication/bytes accounting

Runtime requirements:
- Python graphviz package
- Graphviz binaries installed and on PATH

If Graphviz is not installed, the script prints a clear message and exits.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Tuple

try:
    from graphviz import Digraph
except Exception as exc:
    print("Graphviz Python package not available or Graphviz binaries missing.")
    print("Please install with: pip install graphviz and install Graphviz from https://graphviz.org/download/")
    print(f"Details: {exc}")
    sys.exit(1)


class DiagramStyle:
    """
    Centralized styling helpers to keep a consistent look across diagrams.
    """

    def __init__(self, theme: str = "minimal") -> None:
        # Theme presets
        themes = {
            "minimal": {
                "bg": "white",
                "font": "Helvetica",
                "graph_color": "#E6E6E6",
                "node_border": "#3A3A3A",
                "edge": "#555555",
                "palette": {
                    "semantic": "#5FB3D9:#CFEAF6",
                    "gcn": "#5CB85C:#DFF0D8",
                    "ppo": "#C49BCF:#F1E6F5",
                    "hardware": "#F0AD4E:#FCE5C3",
                    "federation": "#5DA5DA:#D9E8F6",
                    "metrics": "#A889B5:#EDE0F2",
                    "orchestration": "#FFDC5C:#FFF3C6",
                    "comm": "#8CD17D:#E6F4E2",
                    "danger": "#F28E8C:#FBE0DF",
                    "neutral": "#F7F7FB:#FFFFFF",
                },
            },
            "midnight": {
                "bg": "#0F1116",
                "font": "Helvetica",
                "graph_color": "#2A2E39",
                "node_border": "#DADDE7",
                "edge": "#A0A6B8",
                "palette": {
                    "semantic": "#3FA7D6:#1A3240",
                    "gcn": "#3AA76D:#173225",
                    "ppo": "#A272C4:#2A1F33",
                    "hardware": "#F0A23C:#3A2A13",
                    "federation": "#4A90E2:#1A2638",
                    "metrics": "#8C6BB1:#2A1F33",
                    "orchestration": "#E5C84C:#3A3213",
                    "comm": "#81C784:#19321F",
                    "danger": "#E57373:#3A1F1F",
                    "neutral": "#1A1E26:#0F1116",
                },
            },
            "vivid": {
                "bg": "#FFFFFF",
                "font": "Helvetica",
                "graph_color": "#CCCCCC",
                "node_border": "#222222",
                "edge": "#444444",
                "palette": {
                    "semantic": "#2EC4B6:#CBF3F0",
                    "gcn": "#90BE6D:#E7F3DF",
                    "ppo": "#D81159:#FAD5E0",
                    "hardware": "#FF9F1C:#FFE3C2",
                    "federation": "#577590:#DDE6EF",
                    "metrics": "#9B5DE5:#E9D8FD",
                    "orchestration": "#FFD166:#FFF1C9",
                    "comm": "#06D6A0:#CFF8EA",
                    "danger": "#EF476F:#FAD1DC",
                    "neutral": "#F7F7FB:#FFFFFF",
                },
            },
        }

        if theme not in themes:
            theme = "minimal"
        t = themes[theme]

        self.graph_attrs: Dict[str, str] = {
            "dpi": "500",
            "bgcolor": t["bg"],
            "rankdir": "LR",
            "labelloc": "t",
            "fontsize": "12",
            "fontname": t["font"],
            "splines": "spline",
            "nodesep": "0.7",
            "ranksep": "1.0",
            "pad": "0.25",
            "margin": "0.15",
            "color": t["graph_color"],
            "penwidth": "1.0",
        }
        self.node_attrs: Dict[str, str] = {
            "shape": "box",
            "style": "rounded,filled",
            "fontname": t["font"],
            "fontsize": "11",
            "color": t["node_border"],
            "fillcolor": "#F7F7FB",
            "penwidth": "1.2",
            "margin": "0.12,0.08",
        }
        self.edge_attrs: Dict[str, str] = {
            "color": t["edge"],
            "arrowsize": "0.7",
            "fontname": t["font"],
            "fontsize": "10",
            "penwidth": "1.1",
        }

        self.palette: Dict[str, str] = t["palette"]
        self.theme_name = theme

    def new(self, name: str, title: str, rankdir: str = "LR") -> Digraph:
        graph = Digraph(name=name, format="png")
        graph.attr(rankdir=rankdir)
        for k, v in self.graph_attrs.items():
            if k == "rankdir":
                continue
            graph.graph_attr[k] = v
        for k, v in self.node_attrs.items():
            graph.node_attr[k] = v
        for k, v in self.edge_attrs.items():
            graph.edge_attr[k] = v
        graph.attr(label=title)
        return graph

    def legend(self, g: Digraph, items: Dict[str, str]) -> None:
        with g.subgraph(name="cluster_legend") as c:
            c.attr(label="Legend", fontsize="11", color="#DDDDDD", style="rounded,filled", fillcolor="#F9F9F9")
            c.attr(style="rounded")
            for key, color in items.items():
                c.node(f"legend_{key}", key, shape="box", style="rounded,filled", fillcolor=color)

    def node(self, g: Digraph, name: str, label: str, fill: str, shape: str = "box") -> None:
        g.node(name, label, fillcolor=fill, shape=shape)


def _render_both(g: Digraph, basename: str) -> Tuple[str, str]:
    png_path = g.render(filename=basename, cleanup=True)
    pdf_graph = Digraph(name=g.name, format="pdf")
    pdf_graph.graph_attr.update(g.graph_attr)
    pdf_graph.node_attr.update(g.node_attr)
    pdf_graph.edge_attr.update(g.edge_attr)
    pdf_graph.body.extend(g.body)
    pdf_path = pdf_graph.render(filename=basename, cleanup=True)
    return png_path, pdf_path


def diagram_architecture(style: DiagramStyle) -> Tuple[str, str]:
    g = style.new("architecture", "FedSemGNN System Architecture", rankdir="LR")

    with g.subgraph(name="cluster_ingest") as s:
        s.attr(label="Ingestion", color="#DDDDDD", style="rounded")
        style.node(s, "Clients", "🧑‍💻 Clients / Requests", style.palette["neutral"], shape="tab")
        style.node(s, "Semantic", "🔍 Semantic Processing\n(extract vector)", style.palette["semantic"], shape="component")

    with g.subgraph(name="cluster_learn") as l:
        l.attr(label="Learning", color="#DDDDDD", style="rounded")
        style.node(l, "GCN", "🧠 GCN Encoder\n(embeddings)", style.palette["gcn"], shape="hexagon")
        style.node(l, "PPO", "🎯 PPO Agents\n(policy/value)", style.palette["ppo"], shape="box3d")
        style.node(l, "Federation", "🔁 Federated Sync\n(FedAvg + DP)", style.palette["federation"], shape="folder")

    with g.subgraph(name="cluster_exec") as e:
        e.attr(label="Execution", color="#DDDDDD", style="rounded")
        style.node(e, "Provision", "⚙️ Provisioning\n(place service)", style.palette["orchestration"], shape="box")
        style.node(e, "Hardware", "🖧 Edge Servers / Network\n(resources, power)", style.palette["hardware"], shape="box")
        style.node(e, "Metrics", "📈 Metrics Logger\n(latency, fidelity, power, bytes)", style.palette["metrics"], shape="note")

    g.edge("Clients", "Semantic", label="requests", xlabel="JSON/Protobuf")
    g.edge("Semantic", "GCN", label="semantic vector", xlabel="ℝ^d")
    g.edge("GCN", "PPO", label="embeddings", xlabel="node × hid")
    g.edge("PPO", "Provision", label="decision", xlabel="argmax π(a|s)")
    g.edge("Provision", "Hardware", label="deploy")
    g.edge("Provision", "Metrics", label="emit")
    g.edge("PPO", "Federation", label="local params", xlabel="θ_i")
    g.edge("Federation", "PPO", label="global update", xlabel="θ̄")

    style.legend(g, {
        "Semantic": style.palette["semantic"],
        "GCN": style.palette["gcn"],
        "PPO": style.palette["ppo"],
        "Federation": style.palette["federation"],
        "Execution": style.palette["orchestration"],
        "Hardware": style.palette["hardware"],
        "Metrics": style.palette["metrics"],
    })

    return _render_both(g, os.path.join(os.getcwd(), f"architecture_{style.theme_name}"))


def diagram_federated_cycle(style: DiagramStyle) -> Tuple[str, str]:
    g = style.new("federated_cycle", "Federated Learning Cycle", rankdir="LR")

    style.node(g, "LocalTrain", "🧩 Local Experience\ncollect + PPO update", style.palette["ppo"], shape="box") 
    style.node(g, "Sync", "🔗 Synchronize\n(FedAvg)", style.palette["federation"], shape="folder") 
    style.node(g, "DP", "🛡️ Privacy Noise\n(DP)", style.palette["danger"], shape="octagon") 
    style.node(g, "Broadcast", "📡 Broadcast Global\nWeights", style.palette["federation"], shape="folder") 

    g.edge("LocalTrain", "Sync", label="upload weights", xlabel="θ_i")
    g.edge("Sync", "DP", label="aggregate", xlabel="Σ w_i θ_i")
    g.edge("DP", "Broadcast", label="add noise", xlabel="+ 𝒩(0,σ)")
    g.edge("Broadcast", "LocalTrain", label="download global", xlabel="θ̄")

    return _render_both(g, os.path.join(os.getcwd(), f"federated_cycle_{style.theme_name}"))


def diagram_data_flow(style: DiagramStyle) -> Tuple[str, str]:
    g = style.new("data_flow", "Data Flow: Request to Decision", rankdir="LR")

    style.node(g, "Req", "📥 Service Request", style.palette["neutral"], shape="tab") 
    style.node(g, "Sem", "🔍 Semantic Vector", style.palette["semantic"], shape="component") 
    style.node(g, "Emb", "🧠 GCN Embedding", style.palette["gcn"], shape="hexagon") 
    style.node(g, "Act", "🎯 PPO Action", style.palette["ppo"], shape="box3d") 
    style.node(g, "Prov", "⚙️ Provision Service", style.palette["orchestration"], shape="box") 
    style.node(g, "Log", "📈 Log Metrics", style.palette["metrics"], shape="note") 

    g.edge("Req", "Sem", xlabel="parse")
    g.edge("Sem", "Emb", xlabel="concat res+sem")
    g.edge("Emb", "Act", xlabel="π(a|s)")
    g.edge("Act", "Prov", xlabel="target server")
    g.edge("Prov", "Log", xlabel="latency, fidelity, power, bytes")

    return _render_both(g, os.path.join(os.getcwd(), f"data_flow_{style.theme_name}"))


def diagram_sequence(style: DiagramStyle) -> Tuple[str, str]:
    g = style.new("sequence", "Sequence: Single Placement", rankdir="TB")

    style.node(g, "S1", "1) 🔍 Extract features", style.palette["semantic"], shape="component") 
    style.node(g, "S2", "2) 🧠 Encode with GCN", style.palette["gcn"], shape="hexagon") 
    style.node(g, "S3", "3) 🎯 PPO selects server", style.palette["ppo"], shape="box3d") 
    style.node(g, "S4", "4) ⚙️ Provision service", style.palette["orchestration"], shape="box") 
    style.node(g, "S5", "5) 📈 Record metrics", style.palette["metrics"], shape="note") 

    g.edge("S1", "S2", xlabel="res+sem")
    g.edge("S2", "S3", xlabel="embed")
    g.edge("S3", "S4", xlabel="action")
    g.edge("S4", "S5", xlabel="measure")

    return _render_both(g, os.path.join(os.getcwd(), f"sequence_{style.theme_name}"))


def diagram_topology(style: DiagramStyle) -> Tuple[str, str]:
    g = style.new("topology", "Deployment Topology: Flat vs Hierarchical", rankdir="TB")

    style.node(g, "Root", "🧭 Central Coordinator", style.palette["federation"], shape="folder") 
    with g.subgraph(name="cluster_flat") as flat:
        flat.attr(label="Flat Federation", color="#999999")
        flat.node("F1", "🖥️ Node A", fillcolor=style.palette["hardware"]) 
        flat.node("F2", "🖥️ Node B", fillcolor=style.palette["hardware"]) 
        flat.node("F3", "🖥️ Node C", fillcolor=style.palette["hardware"]) 
        flat.edge("F1", "F2", label="peering")
        flat.edge("F2", "F3", label="peering")

    with g.subgraph(name="cluster_hier") as hier:
        hier.attr(label="Hierarchical Federation", color="#999999")
        hier.node("H1", "🏘️ Cluster 1", fillcolor=style.palette["hardware"]) 
        hier.node("H2", "🏘️ Cluster 2", fillcolor=style.palette["hardware"]) 
        hier.node("H1a", "🖥️ Node 1A", fillcolor=style.palette["hardware"]) 
        hier.node("H1b", "🖥️ Node 1B", fillcolor=style.palette["hardware"]) 
        hier.node("H2a", "🖥️ Node 2A", fillcolor=style.palette["hardware"]) 
        hier.edge("H1a", "H1b", label="local")
        hier.edge("H1", "H2", label="inter-cluster")

    g.edge("Root", "F1", label="global sync")
    g.edge("Root", "H1", label="global sync")

    return _render_both(g, os.path.join(os.getcwd(), f"topology_{style.theme_name}"))


def diagram_activity(style: DiagramStyle) -> Tuple[str, str]:
    g = style.new("activity", "Activity/State Lifecycles", rankdir="LR")

    style.node(g, "Idle", "⏸️ Idle", style.palette["neutral"], shape="ellipse") 
    style.node(g, "Compute", "⚙️ Compute Local Update", style.palette["ppo"], shape="box") 
    style.node(g, "Sync", "🔗 Sync/FedAvg", style.palette["federation"], shape="folder") 
    style.node(g, "Place", "📦 Place Service", style.palette["orchestration"], shape="box") 

    g.edge("Idle", "Compute", label="experience")
    g.edge("Compute", "Sync", label="upload params")
    g.edge("Sync", "Idle", label="download global")
    g.edge("Idle", "Place", label="request arrival")
    g.edge("Place", "Idle", label="complete")

    return _render_both(g, os.path.join(os.getcwd(), f"activity_{style.theme_name}"))


def diagram_component_map(style: DiagramStyle) -> Tuple[str, str]:
    g = style.new("component_map", "Component / Module Map", rankdir="LR")

    style.node(g, "alg", "🧩 src/algorithms\nFedSemGNN, Flat/Hier FedPPO, PPO", style.palette["ppo"], shape="box3d") 
    style.node(g, "core", "🧠 src/core\nconfig, encoders, online learning", style.palette["gcn"], shape="hexagon") 
    style.node(g, "utils", "🔧 src/utils\nsemantic, graph, metrics", style.palette["semantic"], shape="component") 
    style.node(g, "vis", "📈 visualizations\ngenerators", style.palette["metrics"], shape="note") 
    style.node(g, "sim", "🖧 EdgeSimPy\nservers, services", style.palette["hardware"], shape="box") 

    g.edge("alg", "core", label="hyperparams, models")
    g.edge("alg", "utils", label="helpers")
    g.edge("alg", "sim", label="placement decisions")
    g.edge("utils", "vis", label="data → plots")

    return _render_both(g, os.path.join(os.getcwd(), f"component_map_{style.theme_name}"))


def diagram_timing(style: DiagramStyle) -> Tuple[str, str]:
    g = style.new("timing", "Timing / Latency Timeline", rankdir="LR")

    style.node(g, "T1", "🔍 Semantic (ms)", style.palette["semantic"], shape="component") 
    style.node(g, "T2", "🧠 GCN (ms)", style.palette["gcn"], shape="hexagon") 
    style.node(g, "T3", "🎯 PPO (ms)", style.palette["ppo"], shape="box3d") 
    style.node(g, "T4", "⚙️ Provision (ms)", style.palette["orchestration"], shape="box") 
    style.node(g, "T5", "📡 Comm (ms)", style.palette["comm"], shape="folder") 

    g.edge("T1", "T2", xlabel="Δt1")
    g.edge("T2", "T3", xlabel="Δt2")
    g.edge("T3", "T4", xlabel="Δt3")
    g.edge("T4", "T5", xlabel="Δt4")

    return _render_both(g, os.path.join(os.getcwd(), f"timing_{style.theme_name}"))


def diagram_communication(style: DiagramStyle) -> Tuple[str, str]:
    g = style.new("communication", "Communication / Bytes Accounting", rankdir="TB")

    style.node(g, "Params", "📦 Model Params", style.palette["federation"], shape="folder") 
    style.node(g, "Count", "📏 Bytes per Sync", style.palette["comm"], shape="box") 
    style.node(g, "Cum", "📈 Cumulative Bytes", style.palette["metrics"], shape="note") 

    g.edge("Params", "Count", label="size(params)")
    g.edge("Count", "Cum", label="sum over syncs")

    return _render_both(g, os.path.join(os.getcwd(), f"communication_{style.theme_name}"))


def generate_all() -> None:
    themes = ["minimal", "midnight", "vivid"]
    generators = [
        ("architecture", diagram_architecture),
        ("federated_cycle", diagram_federated_cycle),
        ("data_flow", diagram_data_flow),
        ("sequence", diagram_sequence),
        ("topology", diagram_topology),
        ("activity", diagram_activity),
        ("component_map", diagram_component_map),
        ("timing", diagram_timing),
        ("communication", diagram_communication),
    ]

    for theme in themes:
        style = DiagramStyle(theme=theme)
        for name, fn in generators:
            try:
                png, pdf = fn(style)
                print(f"Generated {name} ({theme}): {os.path.basename(png)}, {os.path.basename(pdf)}")
            except Exception as exc:
                print(f"Failed to generate {name} ({theme}): {exc}")


if __name__ == "__main__":
    generate_all()


