import numpy as np
from numpy import typing as npt

from infrastructure.checksum import Checksum
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

    def transmit(self, bits, interface=None, **kwargs):
        self.sent_bits.append(bits)
        self.calls += 1


class DummyNode(Node):

    def __init__(self, address='0'):
        super().__init__(address)
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
        self.sent_bits = None

    def send(self, bits):
        self.sent_bits = bits


class DummyChecksum(Checksum):

    @property
    def size(self):
        return 1

    def compute(self, bits) -> npt.NDArray[np.uint8]:
        return np.array([1], dtype=np.uint8)
