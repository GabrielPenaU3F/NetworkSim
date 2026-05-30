from src.infrastructure.link_factory import LinkFactory


def test_interfaces_are_created_on_node_creation(dummy_nodes, clean_channel):
    a, b = dummy_nodes
    LinkFactory.create_physical_link(a, b, clean_channel)
    assert len(a.interfaces) == 1
    assert len(b.interfaces) == 1

def test_link_is_attached_to_interfaces(dummy_nodes, clean_channel):
    a, b = dummy_nodes
    link = LinkFactory.create_physical_link(a, b, clean_channel)
    assert a.interfaces[0].link == link
    assert b.interfaces[0].link == link

def test_interfaces_point_to_correct_nodes(dummy_nodes, clean_channel):
    a, b = dummy_nodes
    LinkFactory.create_physical_link(a, b, clean_channel)
    assert a.interfaces[0].node == a
    assert b.interfaces[0].node == b

def test_link_knows_both_interfaces(dummy_nodes, clean_channel):
    a, b = dummy_nodes
    link = LinkFactory.create_physical_link(a, b, clean_channel)
    assert link.iface_a.node == a
    assert link.iface_b.node == b

def test_network_link_interfaces_are_connected_to_edge(linear_network):
    # Cannot use fixture hosts because in that case, interfaces won't get connected
    # Need to manually obtain the nodes from the network
    host_a = linear_network.get_node('192.168.0.1')
    host_b = linear_network.get_node('192.168.0.2')
    edge = linear_network.get_topology_graph().get_edge_to(host_a, host_b)
    assert host_a.interfaces[0].edge == edge
    assert host_b.interfaces[0].edge == edge

def test_network_link_edge_knows_correct_nodes(linear_network, hosts):
    host_a, host_b, _ = hosts
    graph = linear_network.get_topology_graph()
    edge = graph.get_edge_to(host_a, host_b)
    assert edge.get_other_node(host_a) == host_b
    assert edge.get_other_node(host_b) == host_a

def test_physical_link_interfaces_have_no_edge(clean_channel, hosts):
    host_a, host_b, _ = hosts
    LinkFactory.create_physical_link(host_a, host_b, clean_channel)
    assert host_a.interfaces[0].edge is None
    assert host_b.interfaces[0].edge is None
