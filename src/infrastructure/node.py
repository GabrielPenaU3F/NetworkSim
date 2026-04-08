from src.infrastructure.p2p_link import P2PLink
from src.protocol_stack.protocol_stack import ProtocolStack


class Node:

    def __init__(self, name, cfg_manager):
        self.name = name
        self.protocol_stack = ProtocolStack(cfg_manager)
        self.interfaces = []
        self.last_message = None
        self.protocol_stack._handle_message = self._on_receive

    def add_interface(self, interface):
        self.interfaces.append(interface)

    def connect_to(self, other_node, channel):
        P2PLink(self, other_node, channel)

    def send(self, message, interface=0):
        interface = self.interfaces[interface]
        self.protocol_stack.transmit(message, interface)

    def _on_receive(self, message):
        self.last_message = message


    def read(self):
        return self.last_message
