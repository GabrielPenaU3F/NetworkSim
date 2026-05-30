from src.errors import ProtocolError
from src.link_layer.link_layer import LinkLayer
from src.physical_layer.physical_layer import PhysicalLayer
from src.protocol_stack.layer import Layer
from src.system_configurations.config_manager import ConfigManager


class LayerFactory:

    @staticmethod
    def build_dummy_layer(cfg_manager: ConfigManager):
        class DummyLayer(Layer):
            def __init__(self):
                self.lower_layer = LayerFactory.build_physical_layer(cfg_manager)

            def transmit(self, bits, interface=None):
                pass

            def on_receive(self, bits):
                pass

        return DummyLayer()

    @staticmethod
    def build_physical_layer(cfg_manager: ConfigManager):
        config = cfg_manager.physical_layer_config
        config.validate()
        code = config.code_cls(**config.code_params)
        return PhysicalLayer(code)

    @staticmethod
    def build_link_layer(cfg_manager: ConfigManager):
        physical_layer = LayerFactory.build_physical_layer(cfg_manager)
        config = cfg_manager.link_layer_config
        checksum = config.checksum_cls(**config.checksum_params)
        fc = config.frame_config

        link_layer = LinkLayer(checksum, config.max_retries,
                     fc.payload_size, fc.seq_size, fc.checksum_size)
        link_layer.attach_lower(physical_layer)
        return link_layer
