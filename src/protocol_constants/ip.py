from typing import Final

IP_SIZE: Final[int] = 32            # IPv4: 4 parts of 8 bits each
OFFSET_SIZE: Final[int] = 16        # enough to represent offsets up to 64KB
REAL_LENGTH_SIZE: Final[int] = 8    # enough for up to 255 payload bits
PAYLOAD_SIZE: Final[int] = 64       # fixed packet payload default value
TTL_SIZE: Final[int] = 8            # 0-255 jumps (not yet implemented)