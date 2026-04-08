from src.protocol_stack.layer import Layer


class PhysicalLayer(Layer):

    def __init__(self, channel_code):
        self.channel_code = channel_code

    def transmit(self, bits, interface=None):
        encoded_bits = self.channel_code.encode_bits(bits)
        interface.send(encoded_bits)

    def on_receive(self, bits, interface=None):
        decoded_bits = self.channel_code.decode_bits(bits)
        return self._forward_up(decoded_bits, interface)
