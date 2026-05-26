from src.infrastructure.link_factory import LinkFactory
from src.infrastructure.nodes import Host
from src.system_configurations.config_manager import ConfigManager


def make_nodes(channel, top_layer='physical'):
    cfg_manager = ConfigManager(top_layer=top_layer)
    A = Host(cfg_manager)
    B = Host(cfg_manager)
    LinkFactory.create_physical_link(A, B, channel)
    return A, B

def make_triangle_nodes(channel, top_layer='physical'):
    cfg_manager = ConfigManager(top_layer=top_layer)
    A = Host(cfg_manager)
    B = Host(cfg_manager)
    C = Host(cfg_manager)
    LinkFactory.create_physical_link(A, B, channel)
    LinkFactory.create_physical_link(B, C, channel)
    LinkFactory.create_physical_link(C, A, channel)
    return A, B, C