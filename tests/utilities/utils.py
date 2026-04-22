from src.infrastructure.node import Node
from src.system_configurations.config_manager import ConfigManager


def make_nodes(channel):
    cfg_manager = ConfigManager(top_layer='physical')
    A = Node("A", cfg_manager)
    B = Node("B", cfg_manager)
    A.connect_to(B, channel)
    return A, B
