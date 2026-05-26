import pytest

from src.infrastructure.network import Network
from src.system_configurations.config_manager import ConfigManager
from tests.conftest import CleanChannel


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
def dummy_nodes():
    A = DummyNode()
    B = DummyNode()
    return A, B

@pytest.fixture
def simple_network():
    return Network(ConfigManager(top_layer='network'))
