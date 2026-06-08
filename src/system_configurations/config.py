from dataclasses import dataclass, field
from typing import Type

import numpy as np

from src.link_layer.checksum import ParityChecksum, Checksum
from src.network_layer.routing import ShortestPathRouting
from src.physical_layer.channel_codes.channel_codes import NoChannelCode, ChannelCode


@dataclass
class CRCConfig:
    generator: list = field(default_factory=lambda: [1, 1, 0, 1])


@dataclass
class ChecksumConfig:
    cls: Type[Checksum] = ParityChecksum
    params: dict = field(default_factory=dict)

    @classmethod
    def from_crc(cls, crc: CRCConfig):
        from src.link_layer.checksum import CRCChecksum
        return cls(cls=CRCChecksum, params={'generator': crc.generator})


@dataclass
class FrameConfig:
    payload_size: int = 8
    seq_size: int = 8
    checksum_size: int = 4

@dataclass
class PacketConfig:

    payload_size: int = 64
    offset_size: int = 16
    real_length_size: int = 8

    def __post_init__(self):
        if 2 ** self.offset_size < self.payload_size:
            raise ValueError(
                f'An offset size of {self.offset_size} bits cannot represent '
                f'offsets up to a payload size of {self.payload_size} bits'
            )

        min_real_length_size = int(np.ceil(np.log2(self.payload_size + 1)))
        if self.real_length_size < min_real_length_size:
            raise ValueError(f'Real length size should be at least {min_real_length_size} '
                             f'bits to represent {self.payload_size} payload bits')

# ------------- Network infrastructure ------------

@dataclass
class InfrastructureConfig:
    alphabet: str = 'test_16bits_alph'

# -------------- Layer configurations -------------

@dataclass
class PhysicalConfig:
    channel_code: Type[ChannelCode] = NoChannelCode
    code_params: dict = field(default_factory=dict)

    def build_channel_code(self):
        self.channel_code.validate(self.code_params)
        return self.channel_code(**self.code_params)


@dataclass
class LinkConfig:
    max_retries: int = 5
    checksum_cfg: ChecksumConfig = field(default_factory=ChecksumConfig)
    frame_cfg: FrameConfig = field(default_factory=FrameConfig)

    def build_checksum(self):
        params = self.checksum_cfg.params
        self.checksum_cfg.cls.validate(params)
        return self.checksum_cfg.cls(**params)


@dataclass
class NetworkConfig:

    routing: ShortestPathRouting = ShortestPathRouting
    address_size: int = 32
    packet_cfg: PacketConfig = field(default_factory=PacketConfig)

    def __post_init__(self):
        if self.address_size % 8 != 0:
            raise ValueError('Address size must be divisible by 8')
