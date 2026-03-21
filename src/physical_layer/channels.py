import random
from abc import abstractmethod, ABC


class Channel(ABC):

    def __init__(self, channel_code, *args, **kwargs):
        self.channel_code = channel_code

    @abstractmethod
    def transmit(self, codebook, message, **kwargs):
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

    def transmit(self, codebook, message, mode=''):

        # Source encoding
        source_bits = codebook.encode_message(message)

        # Channel encoding
        bits = self.channel_code.encode_bits(source_bits)

        # Transmission
        transmitted_bits = self.apply_noise(bits)

        # Channel decoding
        received_bits = self.channel_code.decode_bits(transmitted_bits)

        if mode == 'raw':
            return received_bits
        else:
            # Source decoding - optional
            return codebook.decode_message(received_bits)

    def invert_bit(self, b):
        return str(int(not int(b)))
