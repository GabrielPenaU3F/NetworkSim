import pytest
import numpy as np

from src.infrastructure.channels import BinarySymmetricChannel
from src.infrastructure.link_factory import LinkFactory
from tests.unit.conftest import DummyNode


@pytest.fixture
def noisy_channel():
    return BinarySymmetricChannel(1)

@pytest.fixture
def make_dummy_nodes():
    def _make(channel):
        A = DummyNode()
        B = DummyNode()
        LinkFactory.create_physical_link(A, B, channel)
        return A, B
    return _make


def test_bits_travel_from_a_to_b(make_dummy_nodes, clean_channel):
    a, b = make_dummy_nodes(clean_channel)
    bits = np.array([1, 0, 1, 0], dtype=np.uint8)
    a.interfaces[0].send(bits)
    assert np.all(b.read() == bits)

def test_bits_travel_from_b_to_a(make_dummy_nodes, clean_channel):
    a, b = make_dummy_nodes(clean_channel)
    bits = np.array([1, 0, 1, 0], dtype=np.uint8)
    b.interfaces[0].send(bits)
    assert np.all(a.read() == bits)

def test_full_noise_flips_all_bits(make_dummy_nodes, noisy_channel):
    a, b = make_dummy_nodes(noisy_channel)
    zeros = np.zeros(100, dtype=np.uint8)
    a.interfaces[0].send(zeros)
    assert np.all(b.read() == 1)

def test_error_rate(make_dummy_nodes):
    p = 0.1
    channel = BinarySymmetricChannel(p, channel_rng=np.random.default_rng(seed=0))
    a, b = make_dummy_nodes(channel)
    zeros = np.zeros(10000, dtype=np.uint8)
    a.interfaces[0].send(zeros)
    received = b.read()
    empirical_p = np.sum(received) / len(received)
    assert abs(empirical_p - p) < 0.02
