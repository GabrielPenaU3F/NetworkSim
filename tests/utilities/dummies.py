class CleanChannel:

    def apply_noise(self, bits):
        return bits


class DummyPhysicalLayer:
    def __init__(self):
        self.upper_layer = None
        self.sent_bits = []
        self.calls = 0

    def attach_upper(self, upper):
        self.upper_layer = upper

    def transmit(self, bits, interface=None):
        self.sent_bits.append(bits)
        self.calls += 1


class DummyNode:
    def __init__(self):
        self.interfaces = []
        self._rx_bits = []

    def add_interface(self, interface):
        self.interfaces.append(interface)

    def on_receive(self, bits, interface=None):
        self._rx_bits.append(bits)

    def read(self):
        if self._rx_bits:
            return self._rx_bits.pop(0)
