import pytest

from errors import NetworkError, AddressError
from infrastructure.nodes.host import Host
from src.system_configurations.config_manager import ConfigManager

class TestHost:

    def test_an_unconnected_host_in_link_layer_cannot_send(self, link_cfg_manager):
        a = Host(link_cfg_manager, '192.168.0.1')
        with pytest.raises(AddressError, match='Destination MAC is not connected to this host'):
            a.send('Hello', destination_mac='02:00:00:00:00:02')

    def test_an_unconnected_host_in_network_layer_cannot_send(self):
        cfg_manager = ConfigManager(top_layer='network')
        a = Host(cfg_manager, '192.168.0.1')
        b = Host(cfg_manager, '192.168.0.2')
        with pytest.raises(NetworkError, match='Routing tables have not been built'):
            a.send('Hello', destination_ip='192.168.0.2')

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
        assert host.address is None

    def test_host_accepts_an_address(self):
        host = Host(ConfigManager(), address='192.168.0.1')
        assert host.address == '192.168.0.1'
