from src.protocol_stack.layer import Layer


class PhysicalLayer(Layer):

    def __init__(self, channel, channel_code):
        self.channel = channel
        self.channel_code = channel_code

    def transmit(self, bits, interface=None):
        encoded_bits = self.channel_code.encode_bits(bits)
        if interface is None:
            # legacy mode
            transmitted_bits = self.channel.apply_noise(encoded_bits)
            return self.channel_code.decode_bits(transmitted_bits)
        else:
            interface.send(encoded_bits)
