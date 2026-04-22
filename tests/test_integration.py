import pytest

from src.infrastructure.channels import BinarySymmetricChannel
from tests.utilities.utils import make_nodes


@pytest.fixture
def clean_channel():
    return BinarySymmetricChannel(0)

@pytest.fixture
def nodes():
    return make_nodes

def test_message_delivery(nodes, clean_channel):
    A, B = nodes(clean_channel)
    A.send("sol")
    received = B.read()
    assert received == "sol"

def test_large_message_delivery(nodes, clean_channel):
    A, B = nodes(clean_channel)
    A.send("sol sol mar viento")
    received = B.read()
    assert received == "sol sol mar viento"