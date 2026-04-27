from src.infrastructure.node import Node
from src.system_configurations.config_manager import ConfigManager


def make_nodes(channel, top_layer='physical'):
    cfg_manager = ConfigManager(top_layer=top_layer)
    A = Node("A", cfg_manager)
    B = Node("B", cfg_manager)
    A.connect_to(B, channel)
    return A, B
