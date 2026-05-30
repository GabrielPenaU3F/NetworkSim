import pytest

from src.errors import NetworkError
from src.network_layer.packets import IPPacket


@pytest.fixture
def example_packet():
    origin = '192.168.0.1'
    destiny = '192.168.0.2'
    payload = [1, 0, 1, 0]
    return IPPacket(origin, destiny, payload)


def test_packet_knows_origin_address(example_packet):
    assert example_packet.origin_address == '192.168.0.1'

def test_packet_knows_destination_address(example_packet):
    assert example_packet.destination_address == '192.168.0.2'

def test_packet_payload(example_packet):
    assert example_packet.payload == [1, 0, 1, 0]

def test_cannot_create_packet_without_origin_address():
    with pytest.raises(NetworkError, match='Origin and Destination addresses must be specified'):
        IPPacket(None, '192.168.0.1', [1, 0])

def test_cannot_create_packet_without_destination_address():
    with pytest.raises(NetworkError, match='Origin and Destination addresses must be specified'):
        IPPacket('192.168.0.1', None, [1, 0])

