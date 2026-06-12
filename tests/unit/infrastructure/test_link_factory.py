import pytest

@pytest.fixture
def two_linked_hosts(two_dummy_hosts, link_factory, mock_graph, clean_channel):
    a, b = two_dummy_hosts
    link_factory.create_link(mock_graph, a, b, clean_channel)
    return a, b


class TestLinkCreation:

    def test_interfaces_are_created_on_both_nodes(self, two_linked_hosts):
        a, b = two_linked_hosts
        assert len(a.interfaces) == 1
        assert len(b.interfaces) == 1

    def test_link_is_attached_to_interfaces(self, two_linked_hosts):
        a, b = two_linked_hosts
        assert a.interfaces[0].link == b.interfaces[0].link

    def test_interfaces_point_to_correct_nodes(self, two_linked_hosts):
        a, b = two_linked_hosts
        assert a.interfaces[0].node == a
        assert b.interfaces[0].node == b

    def test_link_knows_both_interfaces(self, two_linked_hosts):
        a, b = two_linked_hosts
        link = a.interfaces[0].link
        assert link.iface_a.node == a
        assert link.iface_b.node == b


class TestGraphInteraction:

    def test_edge_is_added_with_correct_nodes_and_link(self, two_linked_hosts, mock_graph):
        a, b = two_linked_hosts
        link = a.interfaces[0].link
        mock_graph.add_edge.assert_called_once_with(a, b, link)

    def test_interfaces_are_connected_to_the_edge_returned_by_the_graph(self, two_linked_hosts, mock_graph):
        a, b = two_linked_hosts
        edge = mock_graph.add_edge.return_value
        assert a.interfaces[0].edge == edge
        assert b.interfaces[0].edge == edge


class TestMacAssignment:

    def test_interfaces_receive_mac_addresses(self, two_linked_hosts):
        a, b = two_linked_hosts
        assert a.interfaces[0].mac_address is not None
        assert b.interfaces[0].mac_address is not None

    def test_interfaces_receive_different_mac_addresses(self, two_linked_hosts):
        a, b = two_linked_hosts
        assert a.interfaces[0].mac_address != b.interfaces[0].mac_address

    def test_macs_are_registered_in_the_address_registry(self, two_linked_hosts, address_registry):
        a, b = two_linked_hosts
        assert address_registry.is_mac_registered(a.interfaces[0].mac_address)
        assert address_registry.is_mac_registered(b.interfaces[0].mac_address)
