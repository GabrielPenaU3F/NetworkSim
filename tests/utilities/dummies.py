import numpy as np
from numpy import typing as npt

from infrastructure.checksum import Checksum
from infrastructure.nodes.node import Node
from src.infrastructure.interface import Interface


class CleanChannel:

    def apply_noise(self, bits):
        return bits


class DummyLayer:

    def __init__(self):
        self.upper_layer = None
        self.lower_layer = None
        self.sent_bits = []
        self.sent_kwargs = []
        self.received_bits = None
        self.received_interface = None
        self.received_kwargs = {}
        self.calls = 0

    def attach_upper(self, upper):
        self.upper_layer = upper

    def attach_lower(self, lower):
        self.lower_layer = lower

    def transmit(self, bits, interface=None, **kwargs):
        self.sent_bits.append(bits)
        self.sent_kwargs.append(kwargs)
        self.calls += 1

    def on_receive(self, bits, interface=None, **kwargs):
        self.received_bits = bits
        self.received_interface = interface
        self.received_kwargs = kwargs


class DummyNode(Node):

    def __init__(self, ip_address='0'):
        super().__init__(ip_address)
        self.interfaces = []
        self._rx_bits = []

    def on_receive(self, bits, interface=None):
        self._rx_bits.append(bits)

    def read(self):
        if self._rx_bits:
            return self._rx_bits.pop(0)

    def send(self, message, interface=0, **kwargs) -> None:
        pass


class DummyInterface(Interface):

    def __init__(self, node=None):
        super().__init__(node)
        self.mac_address = '02:00:00:00:00:01'
        self.last_sent_bits = None
        self.sent_bits = []

    def send(self, bits):
        self.last_sent_bits = bits
        self.sent_bits.append(bits)


class DummyChecksum(Checksum):

    @property
    def size(self):
        return 1

    def compute(self, bits) -> npt.NDArray[np.uint8]:
        return np.array([1], dtype=np.uint8)
