import pytest

from infrastructure.nodes.host import Host
from src.network_visualizer import _build_nx_graph


@pytest.fixture
def nx_empty_graph(empty_graph):
    return _build_nx_graph(empty_graph)

@pytest.fixture
def nx_example_graph(example_graph):
    return _build_nx_graph(example_graph)

class TestBuildNxGraph:

    def test_empty_graph_has_no_nodes(self, nx_empty_graph):
        assert nx_empty_graph.number_of_nodes() == 0

    def test_empty_graph_has_no_edges(self, nx_empty_graph):
        assert nx_empty_graph.number_of_edges() == 0

    def test_node_count_matches(self, nx_example_graph):
        assert nx_example_graph.number_of_nodes() == 3

    def test_edge_count_matches(self, nx_example_graph):
        assert nx_example_graph.number_of_edges() == 2

    def test_edges_are_not_duplicated(self, nx_example_graph):
        # Each undirected edge must appear exactly once despite being stored
        # in both directions in NetworkGraph's adjacency list.
        assert nx_example_graph.number_of_edges() == 2

    def test_node_labels_are_ip_addresses(self, nx_example_graph):
        assert set(nx_example_graph.nodes) == {'192.168.0.1', '192.168.0.2', '192.168.0.3'}

    def test_node_without_address_uses_id_as_label(self, network_cfg_manager, empty_graph):
        node = Host(network_cfg_manager, address=None)
        empty_graph.add_node(node)
        G = _build_nx_graph(empty_graph)
        assert id(node) in G.nodes

    def test_correct_neighbors(self, nx_example_graph):
        assert set(nx_example_graph.neighbors('192.168.0.2')) == {'192.168.0.1', '192.168.0.3'}

    def test_isolated_node_has_no_neighbors(self, network_cfg_manager, empty_graph):
        node = Host(network_cfg_manager, address='10.0.0.1')
        empty_graph.add_node(node)
        G = _build_nx_graph(empty_graph)
        assert list(G.neighbors('10.0.0.1')) == []
