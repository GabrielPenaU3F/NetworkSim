from src.infrastructure.p2p_link import P2PLink
from src.protocol_stack.protocol_stack import ProtocolStack


class Node:

    def __init__(self, name, cfg_manager):
        self.name = name
        self.protocol_stack = ProtocolStack(cfg_manager)
        self.interfaces = []
        self._rx_messages = []

    def add_interface(self, interface):
        self.interfaces.append(interface)

    def connect_to(self, other_node, channel):
        P2PLink(self, other_node, channel)

    def send(self, message, interface=0) -> None:
        interface = self.interfaces[interface]
        self.protocol_stack.transmit(message, interface)

    def on_receive(self, bits) -> None:
        message = self.protocol_stack.on_receive(bits)
        if message is not None:
            self._rx_messages.append(message)

    def read(self):
        if self._rx_messages:
            return self._rx_messages.pop(0)
