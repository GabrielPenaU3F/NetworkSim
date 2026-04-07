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

    def send(self, message, interface=0):
        interface = self.interfaces[interface]
        self.protocol_stack.transmit(message, interface)

    def _on_receive(self, message):
        self.last_message = message


class Interface:

    def __init__(self, node, link):
        self.node = node
        self.link = link

    def send(self, bits):
        self.link.transmit(self, bits)

    def receive(self, bits):
        self.node.protocol_stack.receive(bits)