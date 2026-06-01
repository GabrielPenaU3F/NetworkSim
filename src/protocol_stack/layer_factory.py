from src.errors import ProtocolError
from src.link_layer.link_layer import LinkLayer
from src.network_layer.network_layer import NetworkLayer
from src.physical_layer.physical_layer import PhysicalLayer
from src.protocol_stack.layer import Layer
from src.system_configurations.config_manager import ConfigManager


class LayerFactory:

    # THIS IS TO BE USED IN DEVELOPMENT ONLY
    @staticmethod
    def build_dummy_layer(cfg_manager: ConfigManager, **kwargs):
        class DummyLayer(Layer):
            def __init__(self):
                self.lower_layer = LayerFactory.build_physical_layer(cfg_manager)

            def transmit(self, bits, interface=None, **kwargs):
                pass

            def on_receive(self, bits):
                pass

        return DummyLayer()

    @staticmethod
    def build_physical_layer(cfg_manager: ConfigManager, **kwargs):
        config = cfg_manager.physical_layer_cfg
        code = config.build_channel_code()
        return PhysicalLayer(code)

    @staticmethod
    def build_link_layer(cfg_manager: ConfigManager, **kwargs):
        physical_layer = LayerFactory.build_physical_layer(cfg_manager)
        link_cfg = cfg_manager.link_layer_cfg
        checksum = link_cfg.build_checksum()
        fc = link_cfg.frame_cfg

        link_layer = LinkLayer(checksum, link_cfg.max_retries,
                     fc.payload_size, fc.seq_size, fc.checksum_size)
        link_layer.attach_lower(physical_layer)
        return link_layer

    @staticmethod
    def build_network_layer(cfg_manager: ConfigManager, address='127.0.0.1', **kwargs):
        network_layer = NetworkLayer(address)
        link_layer = LayerFactory.build_link_layer(cfg_manager)
        network_layer.attach_lower(link_layer)
        return network_layer