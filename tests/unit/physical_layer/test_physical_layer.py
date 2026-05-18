import numpy as np
import pytest

from src.physical_layer.channel_codes.channel_codes import NoChannelCode, RepetitionChannelCode
from src.physical_layer.physical_layer import PhysicalLayer

class DummyInterface:
    def __init__(self):
        self.sent_bits = None

    def send(self, bits):
        self.sent_bits = bits


class DummyUpper:
    def __init__(self):
        self.received = None

    def on_receive(self, bits):
        self.received = bits


@pytest.fixture
def layer_factory():
    def _make(channel_code):
        return PhysicalLayer(channel_code)
    return _make

@pytest.fixture
def bits():
    return np.tile([0, 1], 4).astype(np.uint8)

class TestPhysicalLayer:

    def test_physical_layer_has_no_lower_layer(self, layer_factory):
        physical = layer_factory(NoChannelCode())
        assert physical.lower_layer is None

    def test_sent_bits(self, layer_factory, bits):
        physical = layer_factory(NoChannelCode())
        interface = DummyInterface()
        physical.transmit(bits, interface)
        assert np.all(interface.sent_bits == bits)

    def test_transmit_encodes_bits(self, layer_factory, bits):
        physical = layer_factory(RepetitionChannelCode(3))
        interface = DummyInterface()
        physical.transmit(bits, interface)
        expected_bits = np.tile([0, 0, 0, 1, 1, 1], 4).astype(np.uint8)
        assert np.all(interface.sent_bits == expected_bits)

    #
    # def test_repetition_improves_error(self, layer_factory):
    #     bits = np.zeros(5000, dtype=np.uint8)
    #     p = 0.2
    #
    #     # codeless
    #     physical_1 = layer_factory(NoChannelCode(), p)
    #     out1 = physical_1.transmit(bits)
    #     err1 = sum(b1 != b2 for b1, b2 in zip(bits, out1))
    #
    #     # with repetition code
    #     physical_2 = layer_factory(RepetitionChannelCode(), p)
    #     out2 = physical_2.transmit(bits)
    #     err2 = sum(b1 != b2 for b1, b2 in zip(bits, out2))
    #
    #     assert err2 < err1