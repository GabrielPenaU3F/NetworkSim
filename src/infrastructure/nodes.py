from abc import abstractmethod, ABC

from src.infrastructure.p2p_link import P2PLink
from src.protocol_stack.protocol_stack import ProtocolStack


class Node(ABC):

    def __init__(self, address=None):
        self.address = address
        self.interfaces = []

    def add_interface(self, interface):
        self.interfaces.append(interface)

    @abstractmethod
    def send(self, message, interface=0) -> None:
        pass

    @abstractmethod
    def on_receive(self, bits, interface=0) -> None:
        pass


class Host(Node):

    def __init__(self, cfg_manager, address=None):
        super().__init__(address)
        self.protocol_stack = ProtocolStack(cfg_manager)
        self._rx_messages = []

    def connect_to(self, other_node, channel):
        P2PLink(self, other_node, channel)

    def send(self, message, interface=0) -> None:
        interface = self.interfaces[interface]
        self.protocol_stack.transmit(message, interface)

    def on_receive(self, bits, interface=None) -> None:
        message = self.protocol_stack.on_receive(bits, interface)
        if message is not None:
            self._rx_messages.append(message)

    def read(self):
        if self._rx_messages:
            return self._rx_messages.pop(0)

    def get_address(self):
        return self.address
