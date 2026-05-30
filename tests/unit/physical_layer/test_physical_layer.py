import numpy as np
import pytest

from src.physical_layer.channel_codes.channel_codes import NoChannelCode, RepetitionChannelCode
from src.physical_layer.physical_layer import PhysicalLayer
from tests.utilities.dummies import DummyInterface


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
