from abc import abstractmethod, ABC


class Node(ABC):

    def __init__(self, address=None):
        self.address = address
        self.interfaces = []
        self.routing_table = None

    def add_interface(self, interface, edge=None):
        if edge is not None:
            interface.connect_edge(edge)
        self.interfaces.append(interface)

    @abstractmethod
    def on_receive(self, bits, interface=0) -> None:
        pass

    def get_interface_for_edge(self, edge):
        for interface in self.interfaces:
            if interface.edge == edge:
                return interface
        return None

    def __eq__(self, other):
        if not isinstance(other, Node): # Validate they're both nodes
            return False
        if self.address is None or other.address is None: # If any does not have an address
            return super().__eq__(other)
        return self.address == other.address # Then compare addresses

    def __hash__(self):
        return hash(self.address)