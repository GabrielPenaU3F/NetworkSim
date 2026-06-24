import pytest

from infrastructure.network import Network
from system_configurations.config_manager import ConfigManager


@pytest.fixture
def make_two_hosts(clean_channel):
    def _make(top_layer):
        cfg_manager = ConfigManager(top_layer=top_layer)
        network = Network(cfg_manager)
        A = network.create_host()
        B = network.create_host()
        network.connect(A, B, clean_channel)
        return A, B
    return _make

@pytest.fixture
def make_triangle_hosts(clean_channel):
    def _make(top_layer):
        cfg_manager = ConfigManager(top_layer=top_layer)
        network = Network(cfg_manager)
        A = network.create_host()
        B = network.create_host()
        C = network.create_host()
        network.connect(A, B, clean_channel)
        network.connect(B, C, clean_channel)
        network.connect(C, A, clean_channel)
        return A, B, C
    return _make
