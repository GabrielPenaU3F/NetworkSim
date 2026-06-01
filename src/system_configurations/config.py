from dataclasses import dataclass, field
from typing import Type

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
    payload_size: int = 64

