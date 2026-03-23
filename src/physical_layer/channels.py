from abc import abstractmethod

import numpy as np


class Channel:

    @abstractmethod
    def apply_noise(self, bits):
        pass

class BinarySymmetricChannel(Channel):

    def __init__(self, probability, rng=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.probability = probability
        self.rng = rng if rng is not None else np.random.default_rng()

    def apply_noise(self, bits):
        bits = np.array([int(b) for b in bits], dtype=np.uint8)
        noise = self.rng.random(len(bits)) < self.probability
        flipped = bits ^ noise.astype(np.uint8)
        return ''.join(flipped.astype(str))
