from src.link_layer.checksum import ParityChecksum
from src.physical_layer.channels import BinarySymmetricChannel
from src.physical_layer.codes.channel_codes import NoChannelCode


def parse_args(config, **kwargs):
    for key, value in kwargs.items():
        if key in config:
            config[key] = value

class Config:

    default_system_configs = {
        'top_layer': 'link'
    }

    default_physical_configs = {
        'error_prob' : 0.05,
        'channel': BinarySymmetricChannel,
        'channel_code': NoChannelCode
    }

    default_link_configs = {
        'block_size': 8,
        'max_retries': 5,
        'checksum': ParityChecksum
    }

    def __init__(self, **kwargs):
        self.system_configs = self.default_system_configs.copy()
        self.physical_configs = self.default_physical_configs.copy()
        self.link_configs = self.default_link_configs.copy()

        self.parse_system_args(**kwargs)
        self.parse_physical_layer_args(**kwargs)
        self.parse_link_layer_args(**kwargs)

    def parse_system_args(self, **kwargs):
        parse_args(self.system_configs, **kwargs)

    def parse_physical_layer_args(self, **kwargs):
        parse_args(self.physical_configs, **kwargs)

    def parse_link_layer_args(self, **kwargs):
        parse_args(self.link_configs, **kwargs)

    def get_system_configs(self):
        return self.system_configs

    def get_physical_layer_configs(self):
        return self.physical_configs

    def get_link_layer_configs(self):
        return self.link_configs