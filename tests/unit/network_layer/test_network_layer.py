import pytest

from src.network_layer.network_layer import NetworkLayer


@pytest.fixture
def network_layer():
    return NetworkLayer('192.168.0.1', address_size=32, packet_payload_size=8)

class TestPacketBuilding:

    def test_packet_built(self, network_layer, tile_bits):
        bits = tile_bits(4)
        packets = network_layer._build_packets(bits, '192.168.0.1')
    #     assert len(packets) == 1
