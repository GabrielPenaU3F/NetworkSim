import pytest

from src.infrastructure.channels import BinarySymmetricChannel
from src.infrastructure.node import Node
from src.system_configurations.config_manager import ConfigManager

@pytest.fixture
def clean_channel():
    return BinarySymmetricChannel(0)

@pytest.fixture
def nodes():
    cfg_manager = ConfigManager(top_layer='physical')
    def _make(channel):
        A = Node("A", cfg_manager)
        B = Node("B", cfg_manager)
        A.connect_to(B, channel)
        return A, B
    return _make


def test_link_creates_interfaces(nodes):
    A, B = nodes(None)
    assert len(A.interfaces) == 1
    assert len(B.interfaces) == 1

def test_message_delivery(nodes, clean_channel):
    A, B = nodes(clean_channel)
    A.send("sol")
    received = B.read()
    assert received == "sol"

def test_large_message_delivery(nodes, clean_channel):
    A, B = nodes(clean_channel)
    A.send("sol sol mar viento")
    received = B.read()
    assert received == "sol sol mar viento"

# def test_no_noise(self, bits, layer_factory):
#     physical = layer_factory(NoChannelCode())
#     received = physical.transmit(bits)
#     np.testing.assert_array_equal(received, bits)
