from abc import ABC

from src.link_layer.checksum import ParityChecksum
from src.infrastructure.channels import BinarySymmetricChannel
from src.physical_layer.channel_codes.channel_codes import NoChannelCode


class Config(ABC):

    DEFAULTS = {}

    @classmethod
    def get_defaults(cls):
        return cls.DEFAULTS


class InfrastructureConfig(Config):

    DEFAULTS = {'top_layer': 'link',
                'alphabet': 'test_16bits_alph',
                'channel': {
                    'class': BinarySymmetricChannel,
                    'params': {
                        'error_prob': 0.05,
                        'channel_rng': None
                    }
                }
    }

    def __init__(self, top_layer, alphabet,
                 channel_cls, channel_params):
        self.top_layer = top_layer
        self.alphabet = alphabet
        self.channel_cls = channel_cls
        self.channel_params = channel_params


class PhysicalConfig(Config):

    DEFAULTS = {
        'channel_code': {
            'class': NoChannelCode,
            'params': {}
        }
    }

    def __init__(self, code_cls, code_params):
        self.code_cls = code_cls
        self.code_params = code_params

    def validate(self):
        self.code_cls.validate(self.code_params)


class LinkConfig(Config):

    DEFAULTS = {
        'max_retries': 5,
        'frame_params': {
            'payload_size': 8,
            'seq_size': 8,
            'checksum_size': 4,
        },
        'checksum': {
            'class': ParityChecksum,
            'params': {}
        },
    }

    def __init__(self, max_retries, frame_config, checksum_cls, checksum_params):
        self.max_retries = max_retries
        self.frame_config = frame_config
        self.checksum_cls = checksum_cls
        self.checksum_params = checksum_params


class FrameConfig:
    def __init__(self, payload_size, seq_size, checksum_size):
        self.payload_size = payload_size
        self.seq_size = seq_size
        self.checksum_size = checksum_size