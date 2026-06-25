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
def topo_two_hosts_with_switch(link_cfg_manager, clean_channel):
    network = Network(link_cfg_manager)
    host_a = network.create_host()
    host_b = network.create_host()
    switch = network.create_switch()
    network.connect(host_a, switch, clean_channel)
    network.connect(switch, host_b, clean_channel)
    return host_a, host_b, switch

@pytest.fixture
def topo_four_hosts_with_two_switches(link_cfg_manager, clean_channel):
    network = Network(link_cfg_manager)

    host_a = network.create_host()
    host_b = network.create_host()
    switch_ab = network.create_switch()

    host_c = network.create_host()
    host_d = network.create_host()
    switch_cd = network.create_switch()

    network.connect(host_a, switch_ab, clean_channel)
    network.connect(host_b, switch_ab, clean_channel)

    network.connect(host_c, switch_cd, clean_channel)
    network.connect(host_d, switch_cd, clean_channel)

    network.connect(switch_ab, switch_cd, clean_channel)

    return host_a, host_b, switch_ab, host_c, host_d, switch_cd
