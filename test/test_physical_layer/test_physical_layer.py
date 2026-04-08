import numpy as np
import pytest

from src.physical_layer.channel_codes.channel_codes import NoChannelCode, RepetitionChannelCode
from src.physical_layer.physical_layer import PhysicalLayer


@pytest.fixture
def layer_factory():
    def _make(channel_code):
        return PhysicalLayer(channel_code)
    return _make

class TestPhysicalLayer:

    def test_output_length(self, nodes, bits):
        channel = BinarySymmetricChannel(0)
        A, B = nodes(channel)
        A.send(bits)
        received_bits = B.read()
        assert len(received_bits) == len(bits)

    def test_no_noise(self, bits, layer_factory):
        physical = layer_factory(NoChannelCode())
        received = physical.transmit(bits)
        np.testing.assert_array_equal(received, bits)

    def test_full_noise(self, bits, layer_factory):
        physical = layer_factory(NoChannelCode())
        received = physical.transmit(bits)
        expected = bits ^ 1
        np.testing.assert_array_equal(received, expected)

    def test_error_rate(self, layer_factory):
        bits = np.zeros(10000, dtype=np.uint8)
        p = 0.1
        physical = layer_factory(NoChannelCode(), p)
        received = physical.transmit(bits)
        errors = sum(1 for b1, b2 in zip(bits, received) if b1 != b2)
        empirical_p = errors / len(bits)
        assert abs(empirical_p - p) < 0.02

    def test_repetition_improves_error(self, layer_factory):
        bits = np.zeros(5000, dtype=np.uint8)
        p = 0.2

        # codeless
        physical_1 = layer_factory(NoChannelCode(), p)
        out1 = physical_1.transmit(bits)
        err1 = sum(b1 != b2 for b1, b2 in zip(bits, out1))

        # with repetition code
        physical_2 = layer_factory(RepetitionChannelCode(), p)
        out2 = physical_2.transmit(bits)
        err2 = sum(b1 != b2 for b1, b2 in zip(bits, out2))

        assert err2 < err1