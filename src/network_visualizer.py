import matplotlib.pyplot as plt
import networkx as nx

from src.infrastructure.network_graph import NetworkGraph


def draw_network(graph: NetworkGraph, title: str = "Network Topology", ax=None) -> None:  # pragma: no cover
    """
    Draw a NetworkGraph using matplotlib and networkx.

    Parameters
    ----------
    graph : NetworkGraph
        The network graph to visualize.
    title : str
        Title displayed above the plot.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on. If None, a new figure is created and plt.show() is called.
    """
    G = _build_nx_graph(graph)

    show = ax is None
    if show:
        fig, ax = plt.subplots(figsize=(8, 6))

    pos = nx.spring_layout(G, seed=42)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1800, node_color="#4C9BE8")
    nx.draw_networkx_edges(G, pos, ax=ax, width=1.5, edge_color="#888888")
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color="#1a1a1a", font_weight="bold")

    ax.set_title(title, fontsize=13, pad=12)
    ax.axis("off")

    if show:
        plt.tight_layout()
        plt.show()


def _build_nx_graph(graph: NetworkGraph) -> nx.Graph:
    G = nx.Graph()

    for node in graph.nodes:
        label = node.ip_address if node.ip_address is not None else id(node)
        G.add_node(label)

    visited_edges = set()
    for node in graph.nodes:
        node_label = node.ip_address if node.ip_address is not None else id(node)
        for edge in graph._adjacency[node]:
            edge_id = id(edge)
            if edge_id not in visited_edges:
                visited_edges.add(edge_id)
                other = edge.get_other_node(node)
                other_label = other.ip_address if other.ip_address is not None else id(other)
                G.add_edge(node_label, other_label)

    return G