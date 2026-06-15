from dataclasses import dataclass, field

import numpy as np


@dataclass
class EthernetFrame:

    src_mac: str
    dst_mac: str
    ether_type: int
    payload: np.ndarray = field(default_factory=lambda: [])
    checksum: int = 0
