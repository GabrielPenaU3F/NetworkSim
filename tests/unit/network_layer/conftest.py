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
        real_length = 4
        payload = np.concatenate((np.zeros(4), np.tile([0, 1], 2)))
        packet = IPPacket(origin_address=origin_address, destination_address=destination_address,
                          is_last=is_last, offset=offset, real_length=real_length, payload=payload)
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
        serialized_offset = np.zeros(8).astype(np.uint8)
        serialized_real_length = np.array([0, 1, 0, 0], dtype=np.uint8)
        serialized_payload = tile_bits(4)
        serialized = np.concatenate([
            serialized_origin,
            serialized_destination,
            np.array([is_last], dtype=np.uint8),
            serialized_offset,
            serialized_real_length,
            serialized_payload
        ], dtype=np.uint8)
        return serialized
    return _make

@pytest.fixture
def serialized_last_bits(serialized_bits):
    return serialized_bits(is_last=1)
