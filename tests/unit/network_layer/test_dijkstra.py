import pytest

from src.errors import NetworkError
from src.infrastructure.network_graph import NetworkGraph
from src.network_layer.routing import ShortestPathRouting
from tests.utilities.dummies import DummyNode


@pytest.fixture
def make_routing():
    def _make(graph):
        return ShortestPathRouting(graph)
    return _make

# example_graph is a -- b -- c

def test_first_hops_of_isolated_node_is_empty(make_routing, three_dummy_hosts):
    graph = NetworkGraph()
    routing = make_routing(graph)
    a, _, _ = three_dummy_hosts
    graph.add_node(a)
    first_hops = routing.get_first_hops(a)
    assert first_hops == {}

def test_first_hop_to_direct_neighbor(make_routing, example_graph, three_dummy_hosts):
    a, b, c = three_dummy_hosts
    routing = make_routing(example_graph)
    first_hops = routing.get_first_hops(a)
    assert first_hops[b] == b

def test_first_hop_to_indirect_neighbor(make_routing, example_graph, three_dummy_hosts):
    a, b, c = three_dummy_hosts
    routing = make_routing(example_graph)
    first_hops = routing.get_first_hops(a)
    assert first_hops[c] == b

def test_origin_not_in_first_hops(make_routing, example_graph, three_dummy_hosts):
    a, b, _ = three_dummy_hosts
    routing = make_routing(example_graph)
    first_hops = routing.get_first_hops(a)
    assert a not in first_hops

def test_first_hop_chooses_shortest_path(network_cfg_manager, three_dummy_hosts, make_routing, clean_channel):
    graph = NetworkGraph()
    routing = make_routing(graph)
    a, b, c = three_dummy_hosts
    d = DummyNode(address='192.168.0.4')

    for node in (a, b, c, d):
        graph.add_node(node)

    # A-B-D es 2 saltos, A-C-B-D sería 3 saltos
    graph.add_edge(a, b)
    graph.add_edge(a, c)
    graph.add_edge(b, d)
    graph.add_edge(c, b)

    first_hops = routing.get_first_hops(a)

    assert first_hops[d] == b

def test_unreachable_node_raises_exception(network_cfg_manager, make_routing, three_dummy_hosts, clean_channel):
    graph = NetworkGraph()
    routing = make_routing(graph)
    a, b, _ = three_dummy_hosts
    graph.add_node(a)
    graph.add_node(b)
    err_msg = 'Node 192.168.0.2 is unreachable from 192.168.0.1'
    with pytest.raises(NetworkError, match=err_msg):
        routing.get_first_hops(a)

def test_cache_is_invalidated_when_node_is_added(make_routing, three_dummy_hosts, clean_channel):
    graph = NetworkGraph()
    routing = make_routing(graph)
    a, b, c = three_dummy_hosts
    graph.add_node(a)
    graph.add_node(b)
    graph.add_edge(a, b)

    # Compute to cache distances
    first_hops = routing.get_first_hops(a)
    assert c not in first_hops

    # Add new node
    graph.add_node(c)
    graph.add_edge(b, c)

    first_hops = routing.get_first_hops(a)
    assert c in first_hops

def test_cache_is_invalidated_when_edge_is_added(make_routing, three_dummy_hosts, clean_channel):
    graph = NetworkGraph()
    routing = make_routing(graph)
    a, b, c = three_dummy_hosts
    graph.add_node(a)
    graph.add_node(b)
    graph.add_node(c)
    graph.add_edge(a, b)

    # Compute to cache distances - C should be unreachable
    with pytest.raises(NetworkError):
        routing.get_first_hops(a)

    # Thus we connect C
    graph.add_edge(b, c)

    # C should now be reachable
    first_hops = routing.get_first_hops(a)
    assert first_hops[c] == b