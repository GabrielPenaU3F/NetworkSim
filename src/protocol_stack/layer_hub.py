from src.errors import ProtocolError
from src.link_layer.link_layer import LinkLayer
from src.physical_layer.physical_layer import PhysicalLayer
from src.system_configurations.config_manager import ConfigManager


class LayerHub:

    @staticmethod
    def _connect_layers(upper, lower):

        if upper.lower_layer is not None:
            raise ProtocolError("Upper layer already connected")

        if lower.upper_layer is not None:
            raise ProtocolError("Lower layer already connected")

        upper.attach_lower(lower)
        lower.attach_upper(upper)

    @staticmethod
    def build_physical_layer(cfg_manager: ConfigManager):
        config = cfg_manager.get_physical_layer_config()
        config.validate()
        code = config.code_cls(**config.code_params)
        return PhysicalLayer(code)

    @staticmethod
    def build_link_layer(cfg_manager: ConfigManager):
        physical_layer = LayerHub.build_physical_layer(cfg_manager)
        config = cfg_manager.get_link_layer_config()
        checksum = config.checksum_cls(**config.checksum_params)
        fc = config.frame_config

        link_layer = LinkLayer(checksum, config.max_retries,
                     fc.payload_size, fc.seq_size, fc.checksum_size)
        LayerHub._connect_layers(link_layer, physical_layer)
        return link_layer

    builders = {
        'physical': build_physical_layer,
        'link': build_link_layer,
    }