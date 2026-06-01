from src.protocol_stack.layer import Layer


class NetworkLayer(Layer):

    def __init__(self, address):
        self.address = address

    def transmit(self, bits, interface, destination_address='127.0.0.1', **kwargs):
        packets = self._build_packets(bits, destination_address)

    def on_receive(self, bits):
        pass

    def _build_packets(self, payload, destination_address):
        pass