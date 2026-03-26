from src.link_layer.link import Link
from src.physical_layer.physical_layer import PhysicalLayer
from src.system_configurations.config import PhysicalConfig, LinkConfig


class LayerHub:

    @staticmethod
    def build_physical_layer(config: PhysicalConfig):
        channel = config.channel_cls(**config.channel_params)
        code = config.code_cls(**config.code_params)
        return PhysicalLayer(channel, code)

    @staticmethod
    def build_link_layer(config: LinkConfig, lower: PhysicalLayer):
        checksum = config.checksum_cls(**config.checksum_params)
        fc = config.frame_config
        return Link(lower, checksum, config.max_retries,
                    fc.payload_size, fc.seq_size, fc.checksum_size)