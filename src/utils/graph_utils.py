# graph_utils.py
import networkx as nx
import numpy as np
import torch

def generate_graph(num_nodes, graph_type="mesh"):
    if graph_type == "ring":
        G = nx.cycle_graph(num_nodes)
    elif graph_type == "mesh":
        side = int(np.ceil(np.sqrt(num_nodes)))
        G = nx.grid_2d_graph(side, side)
    else:
        G = nx.random_geometric_graph(num_nodes, radius=0.1)

    if G.number_of_nodes() > num_nodes:
        keep = list(G.nodes())[:num_nodes]
        G = G.subgraph(keep).copy()

    G = nx.convert_node_labels_to_integers(G)
    
    # Use the updated NetworkX API
    try:
        adj = nx.to_scipy_sparse_array(G).tocoo()
    except AttributeError:
        # Fallback for older NetworkX versions
        adj = nx.to_scipy_sparse_matrix(G).tocoo()

    # EDGE_INDEX for GNNs: shape [2, num_edges], used for message passing
    edge_index = torch.tensor(
        np.vstack((adj.row, adj.col)), dtype=torch.long
    )
    # For FedSemGNN, pass edge_index to GNNEncoder (GraphConv)
    return G, edge_index

def partition_clusters(num_nodes, num_clusters):
    labels = np.random.randint(0, num_clusters, size=num_nodes)
    clusters = {i: np.where(labels == i)[0].tolist()
                for i in range(num_clusters)}
    return labels, clusters
