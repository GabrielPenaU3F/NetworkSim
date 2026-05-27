import pytest

from src.infrastructure.network import Network
from src.infrastructure.network_graph import NetworkGraph
from src.system_configurations.config_manager import ConfigManager
from tests.conftest import CleanChannel
from tests.utilities.dummies import DummyNode
from tests.utilities.utils import make_link, make_network_level_hosts

@pytest.fixture
def network_cfg_manager():
    cfg = ConfigManager(top_layer='network')
    return cfg

@pytest.fixture
def dummy_nodes():
    A = DummyNode()
    B = DummyNode()
    return A, B

@pytest.fixture
def simple_network():
    return Network(ConfigManager(top_layer='network'))

@pytest.fixture
def example_graph():
    a, b, c = make_network_level_hosts()
    graph = NetworkGraph()
    graph.add_node(a)
    graph.add_node(b)
    graph.add_node(c)
    graph.add_edge(a, b, make_link(a, b, CleanChannel()))
    graph.add_edge(b, c, make_link(b, c, CleanChannel()))
    return graph
