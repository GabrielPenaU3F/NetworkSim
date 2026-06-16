from dataclasses import dataclass, field

import numpy as np

from infrastructure.checksum import CRCChecksum
from protocol_constants import ethernet
from utils import serialize_mac_address, int_to_bits, bits_to_int


@dataclass
class EthernetFrame:

    src_mac: str
    dst_mac: str
    ether_type: int
    real_length: int
    payload: np.ndarray
    checksum: int = field(default=0, init=False)

    def __post_init__(self):
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> int:
        body = self.serialize_body()
        crc = CRCChecksum()
        return bits_to_int(crc.compute(body))

    def serialize_body(self) -> np.ndarray:
        dst_bits = serialize_mac_address(self.dst_mac, ethernet.MAC_SIZE)
        src_bits = serialize_mac_address(self.src_mac, ethernet.MAC_SIZE)
        ether_type_bits = int_to_bits(self.ether_type, ethernet.ETHER_TYPE_SIZE)
        real_length_bits = int_to_bits(self.real_length, ethernet.REAL_LENGTH_SIZE)
        return np.concatenate([dst_bits, src_bits, ether_type_bits,
                               real_length_bits, self.payload])
