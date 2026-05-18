import numpy as np
import pytest

from src.link_layer.frame import Frame
from src.utils import pad_bits

@pytest.fixture
def frame_to_serialize():
    def _make(seq=0, is_last=1, is_ack=0):
        bits = np.tile([0, 1], 2)
        padded_bits, _ = pad_bits(bits, 8)
        frame = Frame(seq=seq, is_last=is_last, is_ack=is_ack, real_length=4, payload=padded_bits, checksum=[0, 0])
        return frame
    return _make

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

@pytest.fixture
def base_body():
    base_body = np.array([
        0, 0,  # seq (2 bits)
        1,  # is_last
        0, # is_ack
        0, 1, 0, 0,  # real_length = 4
        0, 1, 0, 1, 0, 0, 0, 0  # payload (padded)
    ], dtype=np.uint8)
    return base_body