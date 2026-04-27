from math import cos, sin, pi
from graphviz import Digraph

OUT = "diagramsdotandpython/federated_cycle"

g = Digraph("federated_cycle", filename=OUT, format="pdf", engine="neato")

# ---------- Graph style ----------
g.graph_attr.update(
    overlap="false",
    splines="curved",
    outputorder="edgesfirst",
    margin="0.06",
    pad="0.06",
)

BASE_FSIZE = "9"
NODE_BASE = dict(
    shape="circle", style="filled", fontname="Helvetica",
    fontsize=BASE_FSIZE, width="0.95", height="0.95",
    margin="0.03,0.03", color="#333333"
)

COL = {
    "start":   "#FFE6AD",
    "semantic":"#F8E8A6",
    "gcn":     "#CFE8FF",
    "action":  "#E7F6E8",
    "reward":  "#FBE6F6",
    "ppo":     "#EAD9FF",
    "sync":    "#D6F5EA",
    "global":  "#FBE2DE",
    "end":     "#E9F0FF",
}

# ---------- Circle layout (smaller radius) ----------
R = 1.6
CX, CY = 0.0, 0.0
angles = [90, 38, -14, -66, -118, -170, -222]  # n1..n7 around the ring

def xy(theta_deg, r=R, cx=CX, cy=CY):
    th = theta_deg * pi / 180.0
    return (round(cx + r * cos(th), 4), round(cy + r * sin(th), 4))

def pnode(name, label, fill, pos_xy, **kw):
    x, y = pos_xy
    g.node(name, label=label, fillcolor=fill, pos=f"{x},{y}!", pin="true",
           **{**NODE_BASE, **kw})

# Place START / NEXT just outside the ring
start_x, start_y = xy(112, R + 0.75)
end_x,   end_y   = xy(-112, R + 0.75)

g.node("start_t", "START\n(t)", shape="doublecircle",
       fillcolor=COL["start"], penwidth="2.0",
       color="#1B7F6A", fontcolor="#1B7F6A",
       pos=f"{start_x},{start_y}!", pin="true", fontsize="10")

g.node("end_t1", "NEXT STEP\n(t+1)", shape="Msquare",
       fillcolor=COL["end"], penwidth="2.0",
       color="#355C7D", fontcolor="#355C7D",
       pos=f"{end_x},{end_y}!", pin="true", fontsize="10")

# Ring nodes
names = ["n1","n2","n3","n4","n5","n6","n7"]
labels = [
    "(1)\nSemantic\nEmbedding",
    "(2)\nGCN Topology\nEncoding",
    "(3)\nAction:\nPlace/Migrate",
    "(4)\nReward\n(lat,power,\nfidelity,cost)",
    "(5)\nLocal PPO\nUpdate",
    "(6)\nIntra-cluster\nSync (K_intra)",
    "(7)\nGlobal\nFedAvg + DP",
]
fills = [COL["semantic"], COL["gcn"], COL["action"], COL["reward"], COL["ppo"], COL["sync"], COL["global"]]

for nm, lb, fc, ang in zip(names, labels, fills, angles):
    pnode(nm, lb, fc, pos_xy=xy(ang))

# ---------- Edges (bigger labels) ----------
edge_kw = dict(
    penwidth="1.15", arrowhead="normal",
    fontsize="10", fontname="Helvetica", color="#444444",
    labeldistance="1.1"
)

def link(a, b, color=None, style=None, lw=None, constraint=True, **kwargs):
    attrs = edge_kw.copy()
    if color: attrs["color"] = color
    if style: attrs["style"] = style
    if lw:    attrs["penwidth"] = str(lw)
    attrs["constraint"] = str(constraint).lower()
    attrs.update(kwargs)  # allow label/xlabel/etc.
    g.edge(a, b, **attrs)

# Main flow with inline labels
link("start_t","n1",        color="#1B7F6A", label="input")
link("n1","n2",             label="s")
link("n2","n3",             label="[s,g]")
link("n3","n4",             label="a_t")
link("n4","n5",             label="r_t")
link("n5","n6",             label="local grads")
link("n6","n7",             label="cluster avg")

# --- SINGLE, NON-OVERLAPPING SOLID EDGE n7 -> end_t1 ---
# One curved edge; leave from south-east of n7 and enter north-west of NEXT,
# unconstrained + long len so it stays away from n6->n7 and node 6.
g.edge(
    "n7:se", "end_t1:nw",
    **{
        **edge_kw,
        "label": "broadcast θ",
        "color": "#355C7D",
        "penwidth": "1.6",
        "constraint": "false",
        "len": "5.6",         # increase if you want it even farther from n6->n7
        "splines": "curved",
        "weight": "0"
    }
)

# --- Dashed loopback NEXT -> START with a tight bend (not wide) ---
# Two close bends near the left to keep the arc snug.
lbx = CX - (R + 0.9)
g.node("loop_bend_low",  "", shape="point", width="0.01", height="0.01",
       pos=f"{lbx},{CY - 0.22}!", pin="true", color="#FFFFFF")
g.node("loop_bend_high", "", shape="point", width="0.01", height="0.01",
       pos=f"{lbx},{CY + 0.22}!", pin="true", color="#FFFFFF")

loop_attrs = {**edge_kw, "style": "dashed", "color": "#888888", "penwidth": "1.2",
              "weight": "0", "constraint": "false", "splines": "polyline"}
g.edge("end_t1:w", "loop_bend_low",  **{**loop_attrs, "label": "epoch advance"})
g.edge("loop_bend_low", "loop_bend_high", **loop_attrs)
g.edge("loop_bend_high", "start_t:w", **loop_attrs)

# Optional dotted credit flow
link("n4","n3",            color="#999999", style="dotted", label="credit flow")

# ---------- Legend INSIDE the circle (bottom-center) ----------
# Descriptive legend entries for edges (compact but clear)
LEG_X, LEG_Y = CX, CY - 0.35
with g.subgraph(name="cluster_innerlegend") as RL:
    RL.attr(label=" Legend ", labelloc="t", fontsize="8",
            color="#C9C9C9", style="rounded", penwidth="1.0")

    RL.node("legend_anchor", shape="point", width="0.01", label="", color="#FFFFFF",
            pos=f"{LEG_X},{LEG_Y}!", pin="true")

    RL.node("legend_square", shape="plaintext", pos=f"{LEG_X},{LEG_Y}!", pin="true", label=(f'''<
<table border="1" cellborder="0" cellspacing="0" cellpadding="3">
 <tr><td>
   <table border="0" cellborder="0" cellspacing="1" cellpadding="1">
    <tr><td></td></tr>
    <tr><td></td></tr>
    <tr><td><b><font point-size="8">Node types</font></b></td></tr>
    <tr><td>
     <table border="0" cellborder="1" cellspacing="0" cellpadding="1">
      <tr>
       <td bgcolor="{COL['semantic']}"><font point-size="7">semantic</font></td>
       <td bgcolor="{COL['gcn']}"><font point-size="7">GCN</font></td>
       <td bgcolor="{COL['action']}"><font point-size="7">action</font></td>
       <td bgcolor="{COL['reward']}"><font point-size="7">reward</font></td>
      </tr>
      <tr>
       <td bgcolor="{COL['ppo']}"><font point-size="7">local PPO</font></td>
       <td bgcolor="{COL['sync']}"><font point-size="7">intra sync</font></td>
       <td bgcolor="{COL['global']}"><font point-size="7">global+DP</font></td>
       <td bgcolor="{COL['start']}"><font point-size="7">START</font></td>
      </tr>
     </table>
    </td></tr>

    <tr><td><font point-size="8"><b>Edge flow (descriptions)</b></font></td></tr>
    <tr><td align="left"><font point-size="7">START→(1): task request input enters the orchestrator.</font></td></tr>
    <tr><td align="left"><font point-size="7">(1)→(2): <b>s</b> — semantic vector from embedding (task intent/features).</font></td></tr>
    <tr><td align="left"><font point-size="7">(2)→(3): <b>[s,g]</b> — fused semantic + graph state (topology/context) to policy.</font></td></tr>
    <tr><td align="left"><font point-size="7">(3)→(4): <b>a_t</b> — action: place/migrate service to target node.</font></td></tr>
    <tr><td align="left"><font point-size="7">(4)→(5): <b>r_t</b> — reward computed from latency, power, fidelity, and cost.</font></td></tr>
    <tr><td align="left"><font point-size="7">(5)→(6): <b>local grads</b> — PPO updates aggregated within cluster.</font></td></tr>
    <tr><td align="left"><font point-size="7">(6)→(7): <b>cluster avg</b> — cluster‑level model sent to global server.</font></td></tr>
    <tr><td align="left"><font point-size="7">(7)→NEXT: <b>broadcast θ</b> — updated global weights distributed to edges.</font></td></tr>
    <tr><td align="left"><font point-size="7"><i>Dashed</i>: epoch advance to next step · <i>Dotted</i>: reward credit assignment.</font></td></tr>
   </table>
 </td></tr>
</table>
>'''))

# Invisible nudge to keep legend bonded to interior
g.edge("n3", "legend_anchor", style="invis", weight="8")

# ---------- Render ----------
pdf_path = g.render(cleanup=True)
g.format = "png"
png_path = g.render(filename=OUT, cleanup=True)
print("✅ Saved:", pdf_path)
print("✅ Saved:", png_path)
