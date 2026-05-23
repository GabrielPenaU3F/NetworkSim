import pytest

from src.errors import NetworkError
from src.infrastructure.network_graph import NetworkGraph
from src.infrastructure.nodes import Host
from src.system_configurations.config_manager import ConfigManager


@pytest.fixture
def graph():
    return NetworkGraph()

@pytest.fixture
def hosts():
    cfg = ConfigManager(top_layer='network')
    a = Host(cfg, address='192.168.0.1')
    b = Host(cfg, address='192.168.0.2')
    c = Host(cfg, address='192.168.0.3')
    return a, b, c


def test_graph_starts_empty(graph):
    assert graph.node_count() == 0

def test_add_node(graph, hosts):
    a, _, _ = hosts
    graph.add_node(a)
    assert graph.node_count() == 1

def test_add_duplicate_node_does_not_increase_count(graph, hosts):
    a, _, _ = hosts
    graph.add_node(a)
    graph.add_node(a)
    assert graph.node_count() == 1

def test_add_edge_registers_both_directions(graph, hosts):
    a, b, _ = hosts
    graph.add_node(a)
    graph.add_node(b)
    graph.add_edge(a, b)
    assert b in graph.get_neighbors(a)
    assert a in graph.get_neighbors(b)

def test_get_neighbors_of_isolated_node(graph, hosts):
    a, _, _ = hosts
    graph.add_node(a)
    assert graph.get_neighbors(a) == []

def test_get_neighbors_of_connected_node(graph, hosts):
    a, b, c = hosts
    graph.add_node(a)
    graph.add_node(b)
    graph.add_node(c)
    graph.add_edge(a, b)
    graph.add_edge(a, c)
    neighbors = graph.get_neighbors(a)
    assert b in neighbors
    assert c in neighbors

def test_cannot_create_edges_between_nonexistent_nodes(graph, hosts):
    a, b, _ = hosts
    graph.add_node(a)
    with pytest.raises(ValueError, match='Cannot create an edge between nonexistent nodes'):
        graph.add_edge(a, b)
