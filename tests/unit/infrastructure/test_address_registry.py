import re
import pytest

from src.errors import AddressError
from src.infrastructure.address_registry import AddressRegistry


@pytest.fixture
def registry():
    return AddressRegistry()


class TestIPRegistry:

    def test_arbitrary_ip_is_not_registered_initially(self, registry):
        assert '192.168.0.1' not in registry._ip_registry

    def test_register_valid_ip(self, registry):
        registry.register_ip('192.168.0.1')
        assert '192.168.0.1' in registry._ip_registry

    def test_register_ip_with_wrong_number_of_parts_raises_error(self, registry):
        with pytest.raises(AddressError, match='IP addresses must have 4 parts, got 3'):
            registry.register_ip('192.168.0')

    def test_register_duplicate_ip_raises_error(self, registry):
        registry.register_ip('192.168.0.1')
        with pytest.raises(AddressError, match='IP address 192.168.0.1 already in use'):
            registry.register_ip('192.168.0.1')

    def test_registry_respects_custom_address_size(self):
        registry = AddressRegistry(ip_address_size=24)
        registry.register_ip('192.168.0')
        assert '192.168.0' in registry._ip_registry

    def test_register_ip_with_wrong_parts_for_custom_size_raises_error(self):
        registry = AddressRegistry(ip_address_size=24)
        with pytest.raises(AddressError, match='IP addresses must have 3 parts, got 4'):
            registry.register_ip('192.168.0.1')


class TestMACRegistry:

    MAC_PATTERN = re.compile(r'^[0-9a-f]{2}(:[0-9a-f]{2}){5}$')

    def test_arbitrary_mac_is_not_registered_initially(self, registry):
        assert registry.is_mac_registered('02:00:00:00:00:00') is False

    def test_generate_mac_registers_the_address(self, registry):
        mac = registry.generate_mac()
        assert registry.is_mac_registered(mac) is True

    def test_generated_mac_has_correct_format(self, registry):
        mac = registry.generate_mac()
        assert self.MAC_PATTERN.match(mac)

    def test_successive_macs_are_unique(self, registry):
        macs = {registry.generate_mac() for _ in range(10)}
        assert len(macs) == 10

    def test_generated_macs_use_locally_administered_prefix(self, registry):
        mac = registry.generate_mac()
        assert mac.startswith(AddressRegistry.MAC_PREFIX)