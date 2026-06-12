from src.errors import AddressError


class AddressRegistry:

    MAC_PREFIX = '02:00:00'

    def __init__(self, ip_address_size=32):
        self.ip_address_size = ip_address_size
        self._ip_registry = set()
        self._mac_registry = set()
        self._mac_counter = 0

    # ----- IP -----

    def register_ip(self, address):
        self._validate_ip_format(address)
        self._validate_ip_unique(address)
        self._ip_registry.add(address)

    def is_ip_registered(self, address):
        return address in self._ip_registry

    def _validate_ip_format(self, address):
        expected_parts = self.ip_address_size // 8
        actual_parts = len(address.split('.'))
        if actual_parts != expected_parts:
            raise AddressError(f'IP addresses must have {expected_parts} parts, got {actual_parts}')

    def _validate_ip_unique(self, address):
        if self.is_ip_registered(address):
            raise AddressError(f'IP address {address} already in use')

    # ----- MAC -----

    def generate_mac(self):
        mac = self._build_mac(self._mac_counter)
        self._mac_counter += 1
        self._mac_registry.add(mac)
        return mac

    def is_mac_registered(self, mac):
        return mac in self._mac_registry

    def _validate_mac_unique(self, address):
        if address in self._mac_registry:
            raise AddressError(f'MAC address {address} already in use')

    def _build_mac(self, counter):
        return (f'{self.MAC_PREFIX}:'
                f'{(counter >> 16) & 0xFF:02x}:'
                f'{(counter >> 8) & 0xFF:02x}:'
                f'{counter & 0xFF:02x}')
