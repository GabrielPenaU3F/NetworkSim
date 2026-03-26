from copy import deepcopy

from src.system_configurations.config import PhysicalConfig, LinkConfig, FrameConfig, SystemConfig
from src.system_configurations.parameter_routing import route_param


class ConfigManager:

    def __init__(self, **kwargs):

        # Copy defaults
        system_cfg_dict = deepcopy(SystemConfig.get_defaults())
        physical_cfg_dict = deepcopy(PhysicalConfig.get_defaults())
        link_cfg_dict = deepcopy(LinkConfig.get_defaults())

        # Update those which are provided by parameter
        config_dicts = {
            'system': system_cfg_dict,
            'physical': physical_cfg_dict,
            'link': link_cfg_dict
        }
        for key, value in kwargs.items():
            route_param(config_dicts, key, value)

        # Build configuration objects
        self.system_config = self._build_system_config(system_cfg_dict)
        self.physical_config = self._build_physical_config(physical_cfg_dict)
        self.link_config = self._build_link_config(link_cfg_dict)

    def _build_system_config(self, cfg_dict):
        return SystemConfig(
            top_layer=cfg_dict['top_layer'],
        )

    def _build_physical_config(self, cfg_dict):
        return PhysicalConfig(
            channel_cls=cfg_dict['channel']['class'],
            channel_params=cfg_dict['channel']['params'],
            code_cls=cfg_dict['channel_code']['class'],
            code_params=cfg_dict['channel_code']['params']
        )

    def _build_link_config(self, cfg_dict):
        frame_config = self._build_frame_config(cfg_dict['frame_params'])
        return LinkConfig(
            max_retries=cfg_dict['max_retries'],
            frame_config=frame_config,
            checksum_cls=cfg_dict['checksum']['class'],
            checksum_params=cfg_dict['checksum']['params']
        )

    def _build_frame_config(self, params):
        return FrameConfig(params['payload_size'], params['seq_size'], params['checksum_size'])

    def get_system_config(self):
        return self.system_config

    def get_physical_layer_config(self):
        return self.physical_config

    def get_link_layer_config(self):
        return self.link_config


