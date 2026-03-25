from src.link_layer.checksum import ParityChecksum
from src.physical_layer.channels import BinarySymmetricChannel
from src.physical_layer.codes.channel_codes import NoChannelCode
from copy import deepcopy

from src.system_configurations.config import PhysicalConfig
from src.system_configurations.parameter_routing import route_param


class ConfigManager:

    CONFIG_SECTIONS = {
        'system': 'system_configs',
        'physical': 'physical_configs',
        'link': 'link_configs'
    }

    default_system_configs = {
        'top_layer': 'link'
    }

    default_physical_configs = {
        'channel': {
            'class': BinarySymmetricChannel,
            'params': {
                'error_prob': 0.05,
                'channel_rng': None
            }
        },
        'channel_code': {
            'class': NoChannelCode,
            'params': {}
        }
    }

    default_link_configs = {
        'frame': {
            'payload_size': 8,
            'seq_size': 8,
            'checksum_size': 4,
        },
        'max_retries': 5,
        'checksum': {
            'class': ParityChecksum,
            'params': {}
        },
    }

    system_configs = {}
    physical_configs = {}
    link_configs = {}

    def __init__(self, **kwargs):

        # Determine the default value of each configuration
        for section_attr in self.CONFIG_SECTIONS.values():
            default_arg = f'default_{section_attr}'
            setattr(self, section_attr, deepcopy(getattr(self, default_arg)))

        # Update those which are provided by parameter
        for key, value in kwargs.items():
            route_param(self, key, value)

        # Build configuration objects
        self.physical_config = self._build_physical_config()
        self.link_config = self._build_link_config()


    def _build_physical_config(self):
        cfg = self.physical_configs
        return PhysicalConfig(
            channel_cls=cfg['channel']['class'],
            channel_params=cfg['channel']['params'],
            code_cls=cfg['channel_code']['class'],
            code_params=cfg['channel_code']['params']
        )

    def _build_link_config(self):
        pass

    def get_system_configs(self):
        return self.system_configs

    def get_physical_layer_configs(self):
        return self.physical_configs

    def get_link_layer_configs(self):
        return self.link_configs
