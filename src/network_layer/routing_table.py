from src.errors import NetworkError
from src.infrastructure.interface import Interface
from src.infrastructure.nodes import Node


class RoutingTable:

    def __init__(self, node=None):
        self.node = node
        self._table = {}

    def add_entry(self, destination: Node, interface: Interface):
        self._table[destination] = interface

    def get_interface(self, destination):
        if destination not in self._table:
            raise NetworkError(f'Node {destination.address} is unreachable from {self.node.address}')
        return self._table[destination]