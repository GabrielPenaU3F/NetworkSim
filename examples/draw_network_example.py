from src.network_visualizer import draw_network
from tests.utilities.utils import build_linear_network

network = build_linear_network()
draw_network(network.get_topology_graph(), title="Example linear network")
