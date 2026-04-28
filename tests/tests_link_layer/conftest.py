import numpy as np
import pytest

from src.link_layer.checksum import ParityChecksum
from src.link_layer.frame import Frame
from src.link_layer.link_layer import LinkLayer
from src.protocol_stack.layer_hub import LayerHub
from src.utils import pad_bits


class DummyPhysicalLayer:
    def __init__(self):
        self.upper_layer = None
        self.sent_bits = []
        self.calls = 0

    def attach_upper(self, upper):
        self.upper_layer = upper

    def transmit(self, bits, interface=None):
        self.sent_bits.append(bits)
        self.calls += 1


@pytest.fixture
def tile_bits():
    def _make_tile(n):
        return np.tile([0, 1], n)
    return _make_tile

@pytest.fixture
def example_link_layer():
    dummy_physical = DummyPhysicalLayer()
    checksum = ParityChecksum()
    link_layer = LinkLayer(checksum, seq_size=2, payload_size=8, checksum_size=2)
    LayerHub._connect_layers(link_layer, dummy_physical)
    return link_layer

@pytest.fixture
def frame_to_serialize():
    def _make(is_last=1):
        bits = np.tile([0, 1], 2)
        padded_bits, _ = pad_bits(bits, 8)
        frame = Frame(seq=0, is_last=is_last, real_length=4, payload=padded_bits, checksum=[0, 0])
        return frame
    return _make

@pytest.fixture
def serialized_bits():
    def _make(is_last):
        serialized = np.array([
            0, 0,  # seq
            is_last,  # is_last
            0, 1, 0, 0,  # real_length = 4
            0, 1, 0, 1, 0, 0, 0, 0,  # payload (0101 + padding)
            0, 0  # checksum
        ], dtype=np.uint8)
        return serialized
    return _make

@pytest.fixture
def base_body():
    base_body = np.array([
        0, 0,  # seq (2 bits)
        1,  # is_last
        0, 1, 0, 0,  # real_length = 4
        0, 1, 0, 1, 0, 0, 0, 0  # payload (padded)
    ], dtype=np.uint8)
    return base_body