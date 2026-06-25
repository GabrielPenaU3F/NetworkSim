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
def make_three_hosts(clean_channel):
    def _make(top_layer):
        cfg_manager = ConfigManager(top_layer=top_layer)
        network = Network(cfg_manager)
        A = network.create_host()
        B = network.create_host()
        C = network.create_host()
        network.connect(A, B, clean_channel)
        network.connect(B, C, clean_channel)
        return A, B, C
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

@pytest.fixture
def network_with_switch(link_cfg_manager, clean_channel):
    network = Network(link_cfg_manager)
    host_a = network.create_host(address='192.168.0.1')
    host_b = network.create_host(address='192.168.0.2')
    switch = network.create_switch()
    network.connect(host_a, switch, clean_channel)
    network.connect(switch, host_b, clean_channel)
    return host_a, host_b, switch