from src.infrastructure.alphabets import AlphabetProvider
from src.infrastructure.codebook import Codebook
from src.protocol_stack.layer_factory import LayerFactory


class ProtocolStack:

    LAYER_BUILDERS = {
        'physical': LayerFactory.build_physical_layer,
        'link': LayerFactory.build_link_layer,
        'network': LayerFactory.build_network_layer,
    }

    def __init__(self, cfg_manager, address=None):
        alphabet_name = cfg_manager.infrastructure_cfg.alphabet
        alphabet = AlphabetProvider.provide_alphabet(alphabet_name)

        self.address = address
        self.codebook = Codebook(alphabet)
        self.top_layer = self._build_stack(cfg_manager)
        self.bottom_layer = self._find_bottom_layer()

    def transmit(self, message, interface, destination_address=None):
        source_bits = self.codebook.encode_message(message)
        self.top_layer.transmit(source_bits, interface, destination_address=destination_address)

    def _build_stack(self, cfg_manager):
        top = cfg_manager.top_layer
        builders = type(self).LAYER_BUILDERS
        if top not in builders:
            raise ValueError(f"Unknown top layer: {top}")

        top_builder = builders.get(top)
        top_layer = top_builder(cfg_manager, address=self.address)
        return top_layer

    def _find_bottom_layer(self):
        layer = self.top_layer
        while layer.lower_layer is not None:
            layer = layer.lower_layer
        return layer

    def on_receive(self, bits, interface=None):
        processed_bits = self.bottom_layer.on_receive(bits, interface) # Forward up the layers

        if processed_bits is None:
            return None

        message = self.codebook.decode_message(processed_bits)
        return message

    def get_layer(self, layer_name):
        layer = self.top_layer
        while layer is not None:
            if layer.__class__.__name__.lower().startswith(layer_name):
                return layer
            layer = layer.lower_layer

        raise KeyError(f"Unknown layer: {layer_name}")
