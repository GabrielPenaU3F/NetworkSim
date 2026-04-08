from src.infrastructure.alphabets import AlphabetProvider
from src.infrastructure.codebook import Codebook
from src.protocol_stack.layer_hub import LayerHub


class ProtocolStack:

    def __init__(self, cfg_manager):
        alphabet_name = cfg_manager.get_infrastructure_config().alphabet
        alphabet = AlphabetProvider.provide_alphabet(alphabet_name)
        self.codebook = Codebook(alphabet)
        self.top_layer = self._build_stack(cfg_manager)
        self.bottom_layer = self._find_bottom_layer()

    def transmit(self, message, interface=None):
        source_bits = self.codebook.encode_message(message)
        self.top_layer.transmit(source_bits, interface)

    def _build_stack(self, cfg_manager):
        top = cfg_manager.get_protocol_stack_config().top_layer
        builders = LayerHub.builders
        if top not in builders:
            raise ValueError(f"Unknown top layer: {top}")

        top_builder = builders.get(top)
        top_layer = top_builder(cfg_manager)
        return top_layer

    def _find_bottom_layer(self):
        layer = self.top_layer
        while layer.lower_layer is not None:
            layer = layer.lower_layer
        return layer

    def receive(self, bits):
        processed_bits = self.bottom_layer.on_receive(bits) # Forward up the layers
        message = self.codebook.decode_message(processed_bits)
        return message
