import numpy as np
import pytest

from src.network_layer.packets import IPPacket


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
def serialized_bits():
    def _make(is_last=0, is_ack=0):
        checksum_bit = 1 if is_last ^ is_ack == 0 else 0
        serialized = np.array([
            0, 0,  # seq
            is_last,  # is_last
            is_ack, # is_ack
            0, 1, 0, 0,  # real_length = 4
            0, 1, 0, 1, 0, 0, 0, 0,  # payload (0101 + padding)
            checksum_bit, 0  # checksum
        ], dtype=np.uint8)
        return serialized
    return _make