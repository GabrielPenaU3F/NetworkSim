from abc import abstractmethod

import numpy as np

from src.communications_system.layer import Layer


class Channel(Layer):

    def __init__(self, channel_code, *args, **kwargs):
        self.channel_code = channel_code

    @abstractmethod
    def apply_noise(self, bits):
        pass

class BinarySymmetricChannel(Channel):

    def __init__(self, channel_code, probability, rng=None, *args, **kwargs):
        super().__init__(channel_code, *args, **kwargs)
        self.probability = probability
        self.rng = rng if rng is not None else np.random.default_rng()

    def apply_noise(self, bits):
        bits = np.array([int(b) for b in bits], dtype=np.uint8)
        noise = self.rng.random(len(bits)) < self.probability
        flipped = bits ^ noise.astype(np.uint8)
        return ''.join(flipped.astype(str))

    def transmit(self, bits):

        # Channel encoding
        encoded_bits = self.channel_code.encode_bits(bits)

        # Transmission
        transmitted_bits = self.apply_noise(encoded_bits)

        # Channel decoding
        received_bits = self.channel_code.decode_bits(transmitted_bits)

        return received_bits
