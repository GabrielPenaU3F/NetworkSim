import pytest

from src.infrastructure.channels import BinarySymmetricChannel
from tests.utilities.utils import make_nodes, make_triangle_nodes


@pytest.fixture
def clean_channel():
    return BinarySymmetricChannel(0)

@pytest.fixture
def nodes():
    return make_nodes

@pytest.fixture
def nodes_triangle():
    return make_triangle_nodes

class TestIntegrationPhysicalOnly:

    def test_message_delivery(self, nodes, clean_channel):
        A, B = nodes(clean_channel, top_layer='physical')
        A.send("sol")
        received = B.read()
        assert received == "sol"

    def test_large_message_delivery(self, nodes, clean_channel):
        A, B = nodes(clean_channel, top_layer='physical')
        A.send("sol sol mar viento")
        received = B.read()
        assert received == "sol sol mar viento"


class TestIntegrationUpToLink:

    def test_message_delivery(self, nodes, clean_channel):
        A, B = nodes(clean_channel, top_layer='link')
        A.send("sol")
        received = B.read()
        assert received == "sol"

    def test_medium_message_delivery(self, nodes, clean_channel):
        A, B = nodes(clean_channel, top_layer='link')
        A.send("sol luna")
        received = B.read()
        assert received == "sol luna"

    def test_large_message_delivery(self, nodes, clean_channel):
        A, B = nodes(clean_channel, top_layer='link')
        A.send("sol sol mar viento")
        received = B.read()
        assert received == "sol sol mar viento"

    def test_large_message_triangle_delivery(self, nodes_triangle, clean_channel):
        A, B, C = nodes_triangle(clean_channel, top_layer='link')
        A.send("sol sol mar viento", 0)
        received_B = B.read()
        B.send(received_B, 1)
        received_C = C.read()
        C.send(received_C, 1)
        received = A.read()
        assert received == "sol sol mar viento"
