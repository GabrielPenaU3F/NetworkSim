from abc import abstractmethod, ABC


class Node(ABC):

    def __init__(self, ip_address=None):
        self.ip_address = ip_address
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
        if self.ip_address is None or other.ip_address is None: # If any does not have an address
            return super().__eq__(other)
        return self.ip_address == other.ip_address # Then compare addresses

    def __hash__(self):
        return hash(self.ip_address)