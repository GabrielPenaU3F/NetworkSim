from abc import abstractmethod

import numpy as np


class Channel:

    @abstractmethod
    def apply_noise(self, bits):
        pass

class BinarySymmetricChannel(Channel):

    def __init__(self, error_prob, channel_rng=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_prob = error_prob
        self.rng = channel_rng if channel_rng is not None else np.random.default_rng()

    def apply_noise(self, bits):
        noise = self.rng.random(len(bits)) < self.error_prob
        flipped = bits ^ noise.astype(np.uint8)
        return flipped
