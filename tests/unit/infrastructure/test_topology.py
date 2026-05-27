import pytest


def test_graph_starts_empty(empty_graph):
    assert empty_graph.node_count() == 0

def test_add_node(empty_graph, hosts):
    a, _, _ = hosts
    empty_graph.add_node(a)
    assert empty_graph.node_count() == 1

def test_add_duplicate_node_does_not_increase_count(empty_graph, hosts):
    a, _, _ = hosts
    empty_graph.add_node(a)
    empty_graph.add_node(a)
    assert empty_graph.node_count() == 1

def test_get_edge_to_returns_correct_edge(empty_graph, hosts):
    a, b, _ = hosts
    empty_graph.add_node(a)
    empty_graph.add_node(b)
    empty_graph.add_edge(a, b)
    edge = empty_graph.get_edge_to(a, b)
    assert edge is not None
    assert edge.get_other_node(a) == b

def test_get_edge_to_returns_none_if_not_connected(empty_graph, hosts):
    a, b, c = hosts
    empty_graph.add_node(a)
    empty_graph.add_node(b)
    empty_graph.add_node(c)
    empty_graph.add_edge(a, b)
    assert empty_graph.get_edge_to(a, c) is None

def test_add_edge_registers_both_directions(empty_graph, hosts):
    a, b, _ = hosts
    empty_graph.add_node(a)
    empty_graph.add_node(b)
    empty_graph.add_edge(a, b)
    assert b in empty_graph.get_neighbors(a)
    assert a in empty_graph.get_neighbors(b)

def test_get_neighbors_of_isolated_node(empty_graph, hosts):
    a, _, _ = hosts
    empty_graph.add_node(a)
    assert empty_graph.get_neighbors(a) == []

def test_get_neighbors_of_connected_node(example_graph, hosts):
    a, b, c = hosts
    neighbors = example_graph.get_neighbors(b)
    assert a in neighbors
    assert c in neighbors

def test_cannot_create_parallel_edges(empty_graph, hosts):
    a, b, _ = hosts
    empty_graph.add_node(a)
    empty_graph.add_node(b)
    with pytest.raises(ValueError, match='An edge between these nodes already exists'):
        empty_graph.add_edge(a, b)
        empty_graph.add_edge(a, b)

def test_cannot_create_antiparallel_edges(empty_graph, hosts):
    a, b, _ = hosts
    empty_graph.add_node(a)
    empty_graph.add_node(b)
    with pytest.raises(ValueError, match='An edge between these nodes already exists'):
        empty_graph.add_edge(a, b)
        empty_graph.add_edge(b, a)
