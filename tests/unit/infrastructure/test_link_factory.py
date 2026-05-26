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