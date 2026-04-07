from src.protocol_stack.layer import Layer


class PhysicalLayer(Layer):

    def __init__(self, channel, channel_code):
        self.channel = channel
        self.channel_code = channel_code

    def transmit(self, bits):
        encoded_bits = self.channel_code.encode_bits(bits)
        transmitted_bits = self.channel.apply_noise(encoded_bits)
        received_bits = self.channel_code.decode_bits(transmitted_bits)
        return received_bits
