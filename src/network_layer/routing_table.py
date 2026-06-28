from src.errors import NetworkError
from src.infrastructure.interface import Interface


class RoutingTable:

    def __init__(self, node=None):
        self.node = node
        self._table = {}

    def add_entry(self, destination_address: str, interface: Interface):
        self._table[destination_address] = interface

    def get_interface_to_address(self, destination_address):
        if destination_address not in self._table:
            raise NetworkError(f'Node {destination_address} is unreachable from {self.node.ip_address}')
        return self._table[destination_address]