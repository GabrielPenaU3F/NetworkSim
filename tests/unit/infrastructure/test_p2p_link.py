import pytest
import numpy as np

from src.infrastructure.channels import BinarySymmetricChannel
from src.infrastructure.p2p_link import P2PLink

class DummyNode:
    def __init__(self):
        self.interfaces = []
        self._rx_bits = []

    def add_interface(self, interface):
        self.interfaces.append(interface)

    def on_receive(self, bits, interface=None):
        self._rx_bits.append(bits)

    def read(self):
        if self._rx_bits:
            return self._rx_bits.pop(0)

@pytest.fixture
def clean_channel():
    return BinarySymmetricChannel(0)

@pytest.fixture
def noisy_channel():
    return BinarySymmetricChannel(1)

@pytest.fixture
def make_dummy_nodes():
    def _make(channel):
        A = DummyNode()
        B = DummyNode()
        P2PLink(A, B, channel)
        return A, B
    return _make

def test_link_creates_interfaces(make_dummy_nodes, clean_channel):
    A, B = make_dummy_nodes(clean_channel)
    assert len(A.interfaces) == 1
    assert len(B.interfaces) == 1

def test_no_noise(make_dummy_nodes, clean_channel):
    A, B = make_dummy_nodes(clean_channel)
    bits = np.array([1, 0, 1, 0], dtype=np.uint8)
    A.interfaces[0].send(bits)
    assert np.all(B.read() == bits)


def test_full_noise_flips_all_bits(make_dummy_nodes, noisy_channel):
    A, B = make_dummy_nodes(noisy_channel)
    zeros = np.zeros(100, dtype=np.uint8)
    A.interfaces[0].send(zeros)
    assert np.all(B.read() == 1)

def test_error_rate(make_dummy_nodes):
    p = 0.1
    channel = BinarySymmetricChannel(p, channel_rng=np.random.default_rng(seed=0))
    A, B = make_dummy_nodes(channel)
    zeros = np.zeros(10000, dtype=np.uint8)
    A.interfaces[0].send(zeros)
    received = B.read()
    empirical_p = np.sum(received) / len(received)
    assert abs(empirical_p - p) < 0.02
