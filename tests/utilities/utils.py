from src.infrastructure.node import Node
from src.system_configurations.config_manager import ConfigManager


def make_nodes(channel, top_layer='physical'):
    cfg_manager = ConfigManager(top_layer=top_layer)
    A = Node("A", cfg_manager)
    B = Node("B", cfg_manager)
    A.connect_to(B, channel)
    return A, B

def make_triangle_nodes(channel, top_layer='physical'):
    cfg_manager = ConfigManager(top_layer=top_layer)
    A = Node("A", cfg_manager)
    B = Node("B", cfg_manager)
    C = Node("C", cfg_manager)
    A.connect_to(B, channel)
    B.connect_to(C, channel)
    C.connect_to(A, channel)
    return A, B, C