from dataclasses import dataclass, field
from typing import Type

import numpy as np

from src.link_layer.checksum import Checksum, ParityChecksum


@dataclass
class Frame:

    seq: int = 0
    is_last: int = 0
    is_ack: int = 0
    real_length: int = 0
    payload: np.ndarray = field(default_factory=lambda: [])
    checksum: Type[Checksum] = ParityChecksum

    def get_true_payload(self):
        return self.payload[:self.real_length]
