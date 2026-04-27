# diagram_generator.py
import graphviz
import matplotlib.pyplot as plt

def save_graphviz_diagram(dot_source, filename_base):
    # Render with Graphviz (architecture, workflow, etc.)
    dot = graphviz.Source(dot_source)
    # Save as PDF
    dot.render(f"{filename_base}.pdf", format="pdf", cleanup=True)
    # Save as PNG (500 DPI)
    dot.render(f"{filename_base}.png", format="png", cleanup=True, renderer='cairo', dpi=500)

def save_matplotlib_plot(fig, filename_base):
    # Save as PDF
    fig.savefig(f"{filename_base}.pdf", bbox_inches='tight')
    # Save as PNG (500 DPI)
    fig.savefig(f"{filename_base}.png", dpi=500, bbox_inches='tight')

# Example: System Architecture (Graphviz DOT)
architecture_dot = """
digraph G {
    rankdir=LR;
    node [shape=box, style=filled, fillcolor=lightgray];
    User1 [label=\"User\"];
    Edge1 [label=\"Edge Server\"];
    Cloud [label=\"Cloud\"];
    User1 -> Edge1 [label=\"Data/Model Update\"];
    Edge1 -> Cloud [label=\"Aggregated Model\"];
    Cloud -> Edge1 [label=\"Global Model\"];
    Edge1 -> User1 [label=\"Personalized Model\"];
}
"""
save_graphviz_diagram(architecture_dot, "System_Diagrams/architecture")

# Example: Performance Plot (Matplotlib)
fig, ax = plt.subplots()
algos = ['FedSemGNN', 'FlatFedPPO', 'HierFedPPO', 'HSQF', 'RandomPlacement']
rewards = [0.19, -0.64, -0.49, -0.48, -0.63]
ax.bar(algos, rewards)
ax.set_ylabel('Reward Mean')
ax.set_title('Algorithm Reward Comparison')
save_matplotlib_plot(fig, "system_diagrams/reward_comparison")
plt.close(fig)