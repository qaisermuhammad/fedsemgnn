# refined_fedsemgnn_framework.py
# Usage:
#   pip install graphviz
#   (Install Graphviz from https://graphviz.org and ensure `dot` is on PATH)
#   python refined_fedsemgnn_framework.py

from graphviz import Digraph

g = Digraph('FedSemGNN_Framework_Refined', filename='fedsemgnn_framework_refined', format='png')

# ---------- Global style ----------
g.attr(rankdir='LR', splines='ortho', fontname='Inter,Helvetica,Arial', fontsize='11')
g.graph_attr.update(dpi='600', pad='0.25', nodesep='0.40', ranksep='0.70')
g.node_attr.update(style='rounded,filled', color='#222222', penwidth='1.2',
                   fontname='Inter,Helvetica,Arial', fontsize='10')
g.edge_attr.update(color='#222222', arrowsize='0.90', penwidth='1.15')

# ---------- Start: IoT devices with icons (HTML-like label) ----------
iot_label = r'''<
<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
  <TR>
    <TD><IMG SRC="icons/phone.png" SCALE="TRUE" WIDTH="28" HEIGHT="28"/></TD>
    <TD><IMG SRC="icons/sensor.png" SCALE="TRUE" WIDTH="28" HEIGHT="28"/></TD>
    <TD><IMG SRC="icons/car.png" SCALE="TRUE" WIDTH="28" HEIGHT="28"/></TD>
  </TR>
  <TR><TD COLSPAN="3" ALIGN="center"><B>IoT / User Devices</B><BR/>(AR/VR, phones, sensors — simulated)</TD></TR>
</TABLE>
>'''
g.node('iot', label=iot_label, shape='none')

# ---------- Semantic front-end ----------
g.node('enc',  'Semantic Encoder',            shape='box', fillcolor='#F6E3B3')
g.node('emb',  'Semantic Embedding',          shape='box', fillcolor='#D9D9D9')

g.edge('iot', 'enc')
g.edge('enc', 'emb')

# ---------- Cluster 1 (Blue dashed): Edge nodes → PPO → Intra-sync ----------
with g.subgraph(name='cluster_1') as c1:
    c1.attr(label='Cluster 1', style='dashed', color='#3B82F6', penwidth='1.35', fontsize='11')
    c1.node('c1_a',    'Edge Node A',                  shape='box',      fillcolor='#BFE1FF')
    c1.node('c1_b',    'Edge Node B',                  shape='box',      fillcolor='#BFE1FF')
    c1.node('c1_ppo',  'Local PPO Agent',              shape='hexagon',  fillcolor='#E7C3E9')
    c1.node('c1_sync', 'Intra-cluster Sync  K₁_intra', shape='box',      fillcolor='#E9EEF9')

    # a simple left-to-right inside cluster
    c1.edge('c1_a', 'c1_ppo')
    c1.edge('c1_b', 'c1_ppo')
    c1.edge('c1_ppo', 'c1_sync', style='dashed')

# ---------- Cluster 2 (Green dashed): Edge nodes → PPO → Intra-sync ----------
with g.subgraph(name='cluster_2') as c2:
    c2.attr(label='Cluster 2', style='dashed', color='#10B981', penwidth='1.35', fontsize='11')
    c2.node('c2_c',    'Edge Node C',                  shape='box',      fillcolor='#BFEFCF')
    c2.node('c2_d',    'Edge Node D',                  shape='box',      fillcolor='#BFEFCF')
    c2.node('c2_ppo',  'Local PPO Agent',              shape='hexagon',  fillcolor='#E7C3E9')
    c2.node('c2_sync', 'Intra-cluster Sync  K₂_intra', shape='box',      fillcolor='#E9EEF9')

    c2.edge('c2_c', 'c2_ppo')
    c2.edge('c2_d', 'c2_ppo')
    c2.edge('c2_ppo', 'c2_sync', style='dashed')

# Fan-out embeddings into the clusters (kept minimal)
g.edge('emb', 'c1_a')
g.edge('emb', 'c2_c')

# ---------- Federated core (right) ----------
g.node('agg',   'Hierarchical Federated Aggregator', shape='box',       fillcolor='#F9B4A8')  # coral
g.node('dp',    'Differential Privacy (DP)\nNoise Injection', shape='ellipse',  fillcolor='#F8C8D1')
g.node('policy','Global Policy Distribution',        shape='parallelogram', fillcolor='#F6D6C0')
g.node('endn',  'End Node\n(simulated global policy output)', shape='box', fillcolor='#EFEFEF')

# Cluster syncs → aggregator
g.edge('c1_sync', 'agg', xlabel='Δθ₁', fontcolor='#666666')
g.edge('c2_sync', 'agg', xlabel='Δθ₂', fontcolor='#666666')

g.edge('agg', 'dp')
g.edge('dp',  'policy')
g.edge('policy', 'endn')

# ---------- Feedback (purple) ----------
g.edge('policy', 'enc', color='#7C3AED', penwidth='1.35',
       xlabel='feedback', fontcolor='#7C3AED')

# ---------- Render ----------
g.render(cleanup=True)
print("Saved: fedsemgnn_system_framework.png (600 DPI)")
