from src.infrastructure.interface import Interface
from src.infrastructure.nodes import Node


class CleanChannel:

    def apply_noise(self, bits):
        return bits


class DummyLowerLayer:
    def __init__(self):
        self.upper_layer = None
        self.sent_bits = []
        self.calls = 0

    def attach_upper(self, upper):
        self.upper_layer = upper

    def transmit(self, bits, interface=None):
        self.sent_bits.append(bits)
        self.calls += 1


class DummyNode(Node):

    def __init__(self, address='0'):
        super().__init__(address)
        self.interfaces = []
        self._rx_bits = []

    def add_interface(self, interface, **kwargs):
        self.interfaces.append(interface)

    def on_receive(self, bits, interface=None):
        self._rx_bits.append(bits)

    def read(self):
        if self._rx_bits:
            return self._rx_bits.pop(0)

    def send(self, message, interface=0) -> None:
        pass


class DummyInterface(Interface):

    def __init__(self, node=None):
        super().__init__(node)
        self.sent_bits = None

    def send(self, bits):
        self.sent_bits = bits