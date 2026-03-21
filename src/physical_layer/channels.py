import random
from abc import abstractmethod, ABC


class Channel(ABC):

    def __init__(self, channel_code, *args, **kwargs):
        self.channel_code = channel_code

    @abstractmethod
    def transmit(self, codebook, message):
        pass

    @abstractmethod
    def apply_noise(self, msg_bits):
        pass

class BinarySymmetricChannel(Channel):

    def __init__(self, channel_code, probability, *args, **kwargs):
        super().__init__(channel_code, *args, **kwargs)
        self.probability = probability

    def apply_noise(self, msg_bits):
        bits = list(msg_bits)
        for idx, b in enumerate(bits):
            if random.random() < self.probability:
                bits[idx] = self.invert_bit(b)
        return ''.join(bits)

    def transmit(self, codebook, bits):

        # Channel encoding
        encoded_bits = self.channel_code.encode_bits(bits)

        # Transmission
        transmitted_bits = self.apply_noise(encoded_bits)

        # Channel decoding
        received_bits = self.channel_code.decode_bits(transmitted_bits)

        return received_bits

    def invert_bit(self, b):
        return str(int(not int(b)))
