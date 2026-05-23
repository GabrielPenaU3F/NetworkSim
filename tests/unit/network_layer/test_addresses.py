import pytest

from src.errors import NetworkError
from src.infrastructure.nodes import Host
from src.system_configurations.config_manager import ConfigManager


def test_host_default_address_is_none():
    host = Host(ConfigManager())
    assert host.get_address() is None

def test_host_accepts_an_address():
    host = Host(ConfigManager(), address='192.168.0.1')
    assert host.get_address() == '192.168.0.1'

def test_network_host_default_address(basic_network):
    host = basic_network.create_host()
    assert host.get_address() == '192.168.0.1'

def test_cannot_create_two_hosts_with_equal_addresses(basic_network):
    with pytest.raises(NetworkError) as e:
        host_1 = basic_network.create_host(address='192.168.0.1')
        host_2 = basic_network.create_host(address='192.168.0.1')
        assert e.message == 'Address 192.168.0.1 already in use'
