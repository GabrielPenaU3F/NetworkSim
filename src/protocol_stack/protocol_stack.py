from src.infrastructure.alphabets import AlphabetProvider
from src.infrastructure.codebook import Codebook
from src.protocol_stack.layer_hub import LayerHub


class ProtocolStack:

    def __init__(self, cfg_manager):
        alphabet_name = cfg_manager.get_infrastructure_config().alphabet
        alphabet = AlphabetProvider.provide_alphabet(alphabet_name)
        self.codebook = Codebook(alphabet)
        self.top_layer = self._build_stack(cfg_manager)

    def transmit(self, message, interface=None):
        source_bits = self.codebook.encode_message(message)
        if interface is None:
            received_bits = self._transmit_legacy(source_bits)
            return self.codebook.decode_message(received_bits)
        else:
            self._transmit_current(source_bits, interface)


    def _transmit_legacy(self, bits):
        return self.top_layer.transmit(bits)

    def _build_stack(self, cfg_manager):
        top = cfg_manager.get_infrastructure_config().top_layer
        builders = LayerHub.builders
        if top not in builders:
            raise ValueError(f"Unknown top layer: {top}")

        top_builder = builders.get(top)
        top_layer = top_builder(cfg_manager)
        return top_layer

    def _transmit_current(self, bits, interface=None):
        self.top_layer.transmit(bits, interface)

    def receive(self, bits):
        message = self.codebook.decode_message(bits)
        self._handle_message(message)

    def _handle_message(self, message):
        pass