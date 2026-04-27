# gcn_encoder.py

import time
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.utils import add_self_loops, degree
import os

class GCNEncoder(torch.nn.Module):
    """
    GCNEncoder for FedSemGNN and other GNN-based algorithms.
    Expects EDGE_INDEX in [2, num_edges] format for message passing.
    """
    def __init__(self, in_feats, hidden_dim, cache=True):
        super().__init__()
        self.conv1 = GCNConv(in_feats,  hidden_dim, cached=cache)
        self.conv2 = GCNConv(hidden_dim, hidden_dim, cached=cache)
        self.cache = cache
        # buffers to hold the normalized graph
        self.register_buffer("_norm_edge_index", None)
        self.register_buffer("_norm_edge_weight", None)

    def forward(self, x, edge_index):
        num_nodes = x.size(0)

        # one‐time normalization if caching
        if self.cache and self._norm_edge_index is None:
            # add self‐loops
            edge_index, _ = add_self_loops(edge_index, num_nodes=num_nodes)
            row, col = edge_index

            # compute degree
            deg      = degree(col, num_nodes, dtype=x.dtype)
            deg_inv_sqrt = deg.pow(-0.5)
            # normalization: D^{-1/2} A D^{-1/2}
            weight = deg_inv_sqrt[row] * deg_inv_sqrt[col]

            object.__setattr__(self, "_norm_edge_index", edge_index)
            object.__setattr__(self, "_norm_edge_weight", weight)

        idx = self._norm_edge_index if self.cache else edge_index
        w   = self._norm_edge_weight if self.cache else None

        # time just the sparse‐multiplication message pass
        t0 = time.time()
        x = self.conv1(x, idx, w)
        x = F.relu(x)
        x = self.conv2(x, idx, w)
        t1 = time.time()

        if os.getenv("GCN_VERBOSE"): 
            print(f"[GCN Debug] message‐pass: {(t1-t0)*1e3:.2f}ms")

        return x


# ──────────────────────────────────────────────────────────────────────────────
# LinearEncoder: simple one‐layer ablation
# ──────────────────────────────────────────────────────────────────────────────

class LinearEncoder(torch.nn.Module):
    def __init__(self, in_feats, hidden_dim):
        super().__init__()
        self.fc = torch.nn.Linear(in_feats, hidden_dim)
    def forward(self, x, edge_index=None):
        # edge_index ignored
        return self.fc(x)
