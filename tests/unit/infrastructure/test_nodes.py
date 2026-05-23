import pytest

from src.errors import NetworkError
from src.infrastructure.nodes import Host
from src.system_configurations.config_manager import ConfigManager

class TestNode:


    def test_hosts_with_equal_addresses_are_the_same(self):
        cfg_manager = ConfigManager()
        a = Host(cfg_manager, '1')
        b = Host(cfg_manager, '1')
        assert a == b

    def test_hosts_with_different_addresses_are_distinct(self):
        cfg_manager = ConfigManager()
        a = Host(cfg_manager, '1')
        b = Host(cfg_manager, '2')
        assert a != b

    def test_hosts_with_no_addresses_are_compared_by_reference(self):
        cfg_manager = ConfigManager()
        a = Host(cfg_manager, None)
        b = Host(cfg_manager, None)
        assert a == a
        assert a != b


class TestAddresses:

    def test_host_default_address_is_none(self):
        host = Host(ConfigManager())
        assert host.get_address() is None

    def test_host_accepts_an_address(self):
        host = Host(ConfigManager(), address='192.168.0.1')
        assert host.get_address() == '192.168.0.1'

    def test_network_host_default_address(self, basic_network):
        host = basic_network.create_host()
        assert host.get_address() == '192.168.0.1'

    def test_cannot_create_two_hosts_with_equal_addresses(self, basic_network):
        with pytest.raises(NetworkError) as e:
            host_1 = basic_network.create_host(address='192.168.0.1')
            host_2 = basic_network.create_host(address='192.168.0.1')
            assert e.message == 'Address 192.168.0.1 already in use'
