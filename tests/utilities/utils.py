from src.infrastructure.interface import Interface
from src.infrastructure.link_factory import LinkFactory
from src.infrastructure.network import Network
from src.infrastructure.nodes import Host
from src.infrastructure.p2p_link import P2PLink
from src.system_configurations.config_manager import ConfigManager
from tests.utilities.dummies import CleanChannel


def make_physical_level_hosts(channel, top_layer='physical'):
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

def make_network_level_hosts():
    cfg = ConfigManager(top_layer='network')
    a = Host(cfg, address='192.168.0.1')
    b = Host(cfg, address='192.168.0.2')
    c = Host(cfg, address='192.168.0.3')
    return a, b, c

def make_link(node_a, node_b, channel):
    iface_a = Interface(node_a)
    iface_b = Interface(node_b)
    link = P2PLink(iface_a, iface_b, channel)
    iface_a.attach_link(link)
    iface_b.attach_link(link)
    return link

def build_linear_network():
    network = Network(ConfigManager(top_layer='network'))
    host_a = network.create_host(address='192.168.0.1')
    host_b = network.create_host(address='192.168.0.2')
    host_c = network.create_host(address='192.168.0.3')
    channel = CleanChannel()
    network.connect(host_a, host_b, channel)
    network.connect(host_b, host_c, channel)
    return network
