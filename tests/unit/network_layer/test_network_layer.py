import pytest

from src.network_layer.network_layer import NetworkLayer


@pytest.fixture
def network_layer():
    return NetworkLayer('192.168.0.1')

class TestPacketBuilding:

    def test_packet_built(self, network_layer, tile_bits):
        bits = tile_bits(4)
        payload_size = 8
