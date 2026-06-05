from dataclasses import dataclass, field

import numpy as np

from src.errors import NetworkError


@dataclass
class IPPacket:

    origin_address: str
    destination_address: str
    is_last: int
    offset: int
    payload: np.ndarray = field(default_factory=lambda: [])

    def __post_init__(self):
        if self.origin_address is None or self.destination_address is None:
            raise NetworkError('Origin and Destination addresses must be specified')
