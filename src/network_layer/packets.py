from dataclasses import dataclass

import numpy as np

from src.errors import NetworkError


@dataclass
class IPPacket:
    origin_address: str
    destination_address: str
    payload: np.ndarray

    def __post_init__(self):
        if self.origin_address is None or self.destination_address is None:
            raise NetworkError('Origin and Destination addresses must be specified')
