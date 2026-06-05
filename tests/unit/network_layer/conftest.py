import numpy as np
import pytest

from src.network_layer.packets import IPPacket
from src.utils import serialize_ip_address


@pytest.fixture
def packet_to_serialize():
    def _make(is_last=1):
        origin_address = '192.168.0.1'
        destination_address = '192.168.0.2'
        offset = 0
        payload = np.tile([0, 1], 2)
        packet = IPPacket(origin_address=origin_address, destination_address=destination_address,
                          is_last=is_last, offset=offset, payload=payload)
        return packet
    return _make

@pytest.fixture
def last_packet(packet_to_serialize):
    return packet_to_serialize(is_last=1)

@pytest.fixture
def serialized_bits(tile_bits):
    def _make(is_last=0):
        serialized_origin = serialize_ip_address('192.168.0.1', 32)
        serialized_destination = serialize_ip_address('192.168.0.2', 32)
        serialized = np.concatenate([
            serialized_origin,
            serialized_destination,
            np.array([is_last], dtype=np.uint8),
            np.zeros(8).astype(np.uint8),
            tile_bits(4)
        ], dtype=np.uint8)
        return serialized
    return _make

@pytest.fixture
def serialized_last_bits(serialized_bits):
    return serialized_bits(is_last=1)
