import random
from abc import abstractmethod, ABC

from src.physical_layer.encoder_decoder import EncoderDecoder


class Channel(ABC):

    @abstractmethod
    def transmit(self, codebook, message, **kwargs):
        pass

    @abstractmethod
    def apply_noise(self, msg_bits):
        pass

class BinarySymmetricChannel(Channel):

    def __init__(self, probability):
        self.probability = probability

    def apply_noise(self, msg_bits):
        bits = list(msg_bits)
        for idx, b in enumerate(bits):
            if random.random() < self.probability:
                bits[idx] = self.invert_bit(b)
        return ''.join(bits)

    def transmit(self, codebook, message, mode=''):
        ed = EncoderDecoder(codebook)
        bits = ed.encode_message(message)
        transmitted_bits = self.apply_noise(bits)
        if mode == 'raw':
            return transmitted_bits
        else:
            return ed.decode_message(transmitted_bits)

    def invert_bit(self, b):
        return str(int(not int(b)))
