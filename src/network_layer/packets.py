from dataclasses import dataclass, field

import numpy as np

from src.errors import NetworkError


@dataclass
class IPPacket:

    origin_address: str
    destination_address: str
    is_last: int
    offset: int
    real_length: int
    payload: np.ndarray = field(default_factory=lambda: [])

    def __post_init__(self):
        if self.origin_address is None or self.destination_address is None:
            raise NetworkError('Origin and Destination addresses must be specified')

    def get_true_payload(self):
        return self.payload[:self.real_length]


@dataclass
class ARPPacket:

    operation: int        # 0 = REQUEST, 1 = REPLY
    sender_mac: str
    sender_ip: str
    target_mac: str       # '00:00:00:00:00:00' when it is unknown
    target_ip: str

    def __post_init__(self):
        if any(f is None for f in [self.operation, self.sender_mac,
                                    self.sender_ip, self.target_mac, self.target_ip]):
            raise NetworkError('All ARP fields must be specified')
