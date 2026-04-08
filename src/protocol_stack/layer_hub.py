from src.link_layer.link_layer import LinkLayer
from src.physical_layer.physical_layer import PhysicalLayer
from src.system_configurations.config_manager import ConfigManager


class LayerHub:

    @staticmethod
    def build_physical_layer(cfg_manager: ConfigManager):
        config = cfg_manager.get_physical_layer_config()
        config.validate()
        code = config.code_cls(**config.code_params)
        return PhysicalLayer(code)

    @staticmethod
    def build_link_layer(cfg_manager: ConfigManager):
        physical = LayerHub.build_physical_layer(cfg_manager)
        config = cfg_manager.get_link_layer_config()
        checksum = config.checksum_cls(**config.checksum_params)
        fc = config.frame_config
        return LinkLayer(physical, checksum, config.max_retries,
                    fc.payload_size, fc.seq_size, fc.checksum_size)

    builders = {
        'physical': build_physical_layer,
        'link': build_link_layer,
    }