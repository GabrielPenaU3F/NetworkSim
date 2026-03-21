def parse_args(config, **kwargs):
    for key, value in kwargs.items():
        if key in config:
            config[key] = value

class Config:

    default_physical_configs = {
        'error_prob' : 0.05,
        'channel_code': 'hamming'
    }

    default_link_configs = {
        'block_size': 8,
        'max_retries': 5,
    }

    def __init__(self, **kwargs):
        self.physical_configs = self.default_physical_configs.copy()
        self.link_configs = self.default_link_configs.copy()

        self.parse_physical_layer_args(**kwargs)
        self.parse_link_layer_args(**kwargs)

    def parse_link_layer_args(self, **kwargs):
        parse_args(self.link_configs, **kwargs)

    def parse_physical_layer_args(self, **kwargs):
        parse_args(self.physical_configs, **kwargs)

    def get_physical_layer_configs(self):
        return self.physical_configs