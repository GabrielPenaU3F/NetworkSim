import pytest

from src.errors import NetworkError
from src.network_layer.routing_table import RoutingTable
from tests.utilities.dummies import DummyNode


@pytest.fixture
def routing_table():
    return RoutingTable()

def test_routing_table_is_initialized_empty(routing_table):
    assert routing_table._table == {}

def test_destination_added_to_table(routing_table, dummy_interface):
    routing_table.add_entry('192.168.0.1', dummy_interface)
    assert routing_table.get_interface_to_address('192.168.0.1') == dummy_interface

def test_unreachable_node_is_rejected(dummy_interface):
    node_a = DummyNode(ip_address='192.168.0.1')
    routing_table = RoutingTable(node_a)
    routing_table.add_entry('192.168.0.2', dummy_interface)

    err_msg = 'Node 192.168.0.3 is unreachable from 192.168.0.1'
    assert routing_table.get_interface_to_address('192.168.0.2') == dummy_interface
    with pytest.raises(NetworkError, match=err_msg):
        routing_table.get_interface_to_address('192.168.0.3')
