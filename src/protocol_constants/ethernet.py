from typing import Final

MIN_PAYLOAD_BITS: Final[int] = 46 * 8  # 368 bits
MAX_PAYLOAD_BITS: Final[int] = 1500 * 8  # 12000 bits
MAC_SIZE: Final[int] = 48
ETHER_TYPE_SIZE: Final[int] = 16
REAL_LENGTH_SIZE: Final[int] = 16
CHECKSUM_SIZE: Final[int] = 32
