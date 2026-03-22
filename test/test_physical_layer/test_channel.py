import numpy as np
import pytest

from src.physical_layer.alphabets.alphabets import AlphabetProvider
from src.physical_layer.channels import BinarySymmetricChannel
from src.physical_layer.codebook import Codebook
from src.physical_layer.codes.channel_codes import NoChannelCode, RepetitionChannelCode

@pytest.fixture
def bits():
    return "0101010101010101"

@pytest.fixture
def channel_factory():
    def _make(channel_code, p, seed=0):
        rng = np.random.default_rng(seed)
        return BinarySymmetricChannel(channel_code, p, rng=rng)
    return _make

class TestBinarySymmetricChannel:

    def test_output_length(self, bits, channel_factory):
        ch = channel_factory(NoChannelCode(), 0.1)
        received = ch.transmit(bits)
        assert len(received) == len(bits)

    def test_no_noise(self, bits, channel_factory):
        ch = channel_factory(NoChannelCode(), 0.0)
        received = ch.transmit(bits)
        assert received == bits

    def test_full_noise(self, bits, channel_factory):
        ch = channel_factory(NoChannelCode(), 1.0)
        received = ch.transmit(bits)
        expected = ''.join('1' if b == '0' else '0' for b in bits)
        assert received == expected

    def test_error_rate(self, channel_factory):
        bits = "0" * 10000
        p = 0.1
        ch = channel_factory(NoChannelCode(), p)
        received = ch.transmit(bits)
        errors = sum(1 for b1, b2 in zip(bits, received) if b1 != b2)
        empirical_p = errors / len(bits)
        assert abs(empirical_p - p) < 0.02

    def test_repetition_improves_error(self, channel_factory):
        bits = "0" * 5000
        p = 0.2

        # codeless
        ch1 = channel_factory(NoChannelCode(), p)
        out1 = ch1.transmit(bits)
        err1 = sum(b1 != b2 for b1, b2 in zip(bits, out1))

        # with repetition code
        ch2 = channel_factory(RepetitionChannelCode(), p)
        out2 = ch2.transmit(bits)
        err2 = sum(b1 != b2 for b1, b2 in zip(bits, out2))

        assert err2 < err1