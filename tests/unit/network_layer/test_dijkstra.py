import pytest

from src.errors import NetworkError
from src.infrastructure.network_graph import NetworkGraph
from src.infrastructure.nodes import Host
from src.network_layer.routing import ShortestPathRouting
from src.system_configurations.config_manager import ConfigManager
from tests.utilities.utils import make_link


@pytest.fixture
def make_routing():
    def _make(graph):
        return ShortestPathRouting(graph)
    return _make

# example_graph is a -- b -- c

def test_first_hops_of_isolated_node_is_empty(make_routing, hosts):
    graph = NetworkGraph()
    routing = make_routing(graph)
    a, _, _ = hosts
    graph.add_node(a)
    first_hops = routing.get_first_hops(a)
    assert first_hops == {}

def test_first_hop_to_direct_neighbor(make_routing, example_graph, hosts):
    a, b, c = hosts
    routing = make_routing(example_graph)
    first_hops = routing.get_first_hops(a)
    assert first_hops[b] == b

def test_first_hop_to_indirect_neighbor(make_routing, example_graph, hosts):
    a, b, c = hosts
    routing = make_routing(example_graph)
    first_hops = routing.get_first_hops(a)
    assert first_hops[c] == b

def test_origin_not_in_first_hops(make_routing, example_graph, hosts):
    a, b, _ = hosts
    routing = make_routing(example_graph)
    first_hops = routing.get_first_hops(a)
    assert a not in first_hops

def test_first_hop_chooses_shortest_path(network_cfg_manager, make_routing, clean_channel):
    graph = NetworkGraph()
    routing = make_routing(graph)
    a = Host(network_cfg_manager, address='192.168.0.1')
    b = Host(network_cfg_manager, address='192.168.0.2')
    c = Host(network_cfg_manager, address='192.168.0.3')
    d = Host(network_cfg_manager, address='192.168.0.4')

    for node in (a, b, c, d):
        graph.add_node(node)

    # A-B-D es 2 saltos, A-C-B-D sería 3 saltos
    graph.add_edge(a, b, make_link(a, b, clean_channel))
    graph.add_edge(a, c, make_link(a, c, clean_channel))
    graph.add_edge(b, d, make_link(b, d, clean_channel))
    graph.add_edge(c, b, make_link(c, b, clean_channel))

    first_hops = routing.get_first_hops(a)

    assert first_hops[d] == b

def test_unreachable_node_raises_exception(network_cfg_manager, make_routing, hosts, clean_channel):
    graph = NetworkGraph()
    routing = make_routing(graph)
    a, b, _ = hosts
    graph.add_node(a)
    graph.add_node(b)
    err_msg = 'Node 192.168.0.2 is unreachable from 192.168.0.1'
    with pytest.raises(NetworkError, match=err_msg):
        routing.get_first_hops(a)

def test_cache_is_invalidated_when_node_is_added(make_routing, hosts, clean_channel):
    graph = NetworkGraph()
    routing = make_routing(graph)
    a, b, c = hosts
    graph.add_node(a)
    graph.add_node(b)
    graph.add_edge(a, b, make_link(a, b, clean_channel))

    # Compute to cache distances
    first_hops = routing.get_first_hops(a)
    assert c not in first_hops

    # Add new node
    graph.add_node(c)
    graph.add_edge(b, c, make_link(b, c, clean_channel))

    first_hops = routing.get_first_hops(a)
    assert c in first_hops

def test_cache_is_invalidated_when_edge_is_added(make_routing, hosts, clean_channel):
    graph = NetworkGraph()
    routing = make_routing(graph)
    a, b, c = hosts
    graph.add_node(a)
    graph.add_node(b)
    graph.add_node(c)
    graph.add_edge(a, b, make_link(a, b, clean_channel))

    # Compute to cache distances - C should be unreachable
    with pytest.raises(NetworkError):
        routing.get_first_hops(a)

    # Thus we connect C
    graph.add_edge(b, c, make_link(b, c, clean_channel))

    # C should now be reachable
    first_hops = routing.get_first_hops(a)
    assert first_hops[c] == b