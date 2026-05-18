import pytest
import numpy as np

from src.infrastructure.channels import BinarySymmetricChannel
from tests.utilities.utils import make_nodes


class DummyCodebook:

    def encode_message(self, bits):
        return bits

    def decode_message(self, bits):
        return bits

@pytest.fixture
def clean_channel():
    return BinarySymmetricChannel(0)

@pytest.fixture
def nodes():
    return make_nodes

@pytest.fixture
def no_encoding_nodes():
    def _make(channel):
        dummy = DummyCodebook()
        A, B = make_nodes(channel)
        A.protocol_stack.codebook = dummy
        B.protocol_stack.codebook = dummy
        return A, B
    return _make

@pytest.fixture
def zeros():
    return np.zeros(10000, dtype=np.uint8)

def test_link_creates_interfaces(nodes):
    A, B = nodes(None)
    assert len(A.interfaces) == 1
    assert len(B.interfaces) == 1

def test_no_noise(no_encoding_nodes, clean_channel):
    bits = [1, 0, 1, 0]
    A, B = no_encoding_nodes(clean_channel)
    A.send(bits)
    received = B.read()
    assert np.all(received == bits)

def test_full_noise(no_encoding_nodes, zeros):
    noisy_channel = BinarySymmetricChannel(1)
    A, B = no_encoding_nodes(noisy_channel)
    A.send(zeros)
    received = B.read()

    expected = zeros ^ 1
    assert np.all(received == expected)

def test_error_rate(no_encoding_nodes, zeros):
    p = 0.1
    noisy_channel = BinarySymmetricChannel(p)
    A, B = no_encoding_nodes(noisy_channel)
    A.send(zeros)
    received = B.read()

    errors = sum(1 for b1, b2 in zip(zeros, received) if b1 != b2)
    empirical_p = errors / len(zeros)
    assert abs(empirical_p - p) < 0.02