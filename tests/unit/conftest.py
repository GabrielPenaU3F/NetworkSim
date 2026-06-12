import pytest

from infrastructure.address_registry import AddressRegistry
from infrastructure.link_factory import LinkFactory
from src.infrastructure.network_graph import NetworkGraph
from tests.utilities.dummies import DummyNode, CleanChannel

@pytest.fixture
def address_registry():
    return AddressRegistry()

@pytest.fixture
def link_factory(address_registry):
    return LinkFactory(address_registry)

@pytest.fixture
def two_dummy_hosts():
    A = DummyNode()
    B = DummyNode()
    return A, B

@pytest.fixture
def example_graph(three_dummy_hosts):
    a, b, c = three_dummy_hosts
    graph = NetworkGraph()
    graph.add_node(a)
    graph.add_node(b)
    graph.add_node(c)
    graph.add_edge(a, b)
    graph.add_edge(b, c)
    return graph
