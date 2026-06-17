from dataclasses import dataclass, field

import numpy as np


@dataclass
class EthernetFrame:

    src_mac: str
    dst_mac: str
    ether_type: int
    real_length: int
    payload: np.ndarray
    checksum: int
