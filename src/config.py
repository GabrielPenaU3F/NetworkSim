from src.link_layer.checksum import ParityChecksum
from src.physical_layer.channels import BinarySymmetricChannel
from src.physical_layer.codes.channel_codes import NoChannelCode
from copy import deepcopy


PARAM_MAP = {
    'top_layer': ('system', 'top_layer'),

    'channel': ('physical', 'channel', 'class'),
    'error_prob': ('physical', 'channel', 'params', 'error_prob'),
    'channel_rng': ('physical', 'channel', 'params', 'rng'),
    'channel_code': ('physical', 'channel_code', 'class'),

    'block_size': ('link', 'block_size'),
    'max_retries': ('link', 'max_retries'),
    'checksum': ('link', 'checksum', 'class'),
}

def route_param(config_obj, key, value):
    if key not in PARAM_MAP:
        raise KeyError(f"Unknown config parameter: {key}")

    path = PARAM_MAP[key]
    section = path[0]

    try:
        attr_name = config_obj.CONFIG_SECTIONS[section]
    except KeyError:
        raise KeyError(f"Unknown config section: {section}")

    target = getattr(config_obj, attr_name)

    for p in path[1:-1]:
        if p not in target:
            raise KeyError(f"Invalid config path: {path}")
        target = target[p]

    target[path[-1]] = value

class Config:

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
        'block_size': 8,
        'max_retries': 5,
        'checksum': {
            'class': ParityChecksum,
            'params': {}
        }
    }

    system_configs = {}
    physical_configs = {}
    link_configs = {}

    def __init__(self, **kwargs):
        for section_attr in self.CONFIG_SECTIONS.values():
            default_arg = f'default_{section_attr}'
            setattr(self, section_attr, deepcopy(getattr(self, default_arg)))

        for key, value in kwargs.items():
            route_param(self, key, value)

    def get_system_configs(self):
        return self.system_configs

    def get_physical_layer_configs(self):
        return self.physical_configs

    def get_link_layer_configs(self):
        return self.link_configs