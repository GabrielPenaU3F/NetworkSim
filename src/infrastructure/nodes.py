from abc import abstractmethod, ABC

from src.protocol_stack.protocol_stack import ProtocolStack


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
    def send(self, message, interface=0, destination=None) -> None:
        pass

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


class Host(Node):

    def __init__(self, cfg_manager, address=None):
        super().__init__(address)
        self.protocol_stack = ProtocolStack(cfg_manager)
        self._rx_messages = []

    def send(self, message, interface=0, destination_address=None) -> None:
        if destination_address is not None: # if we are in network layer or above
            interface = self.routing_table.get_interface_to_address(destination_address)
        else: # if we are in physical or link layer
            interface = self.interfaces[interface]
        self.protocol_stack.transmit(message, interface, destination_address)

    def on_receive(self, bits, interface=None) -> None:
        message = self.protocol_stack.on_receive(bits, interface)
        if message is not None:
            self._rx_messages.append(message)

    def read(self):
        if self._rx_messages:
            return self._rx_messages.pop(0)
