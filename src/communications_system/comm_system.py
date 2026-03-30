from src.communications_system.layer_hub import LayerHub


class CommSystem:

    def __init__(self, cfg_manager):
        self.stack = self._build_stack(cfg_manager)

    def transmit(self, codebook, message):

        # Source encoding
        source_bits = codebook.encode_message(message)

        # Transmission
        received_bits = self.stack.transmit(source_bits)

        # Source decoding
        message = codebook.decode_message(received_bits)
        return message

    def _build_stack(self, cfg_manager):
        top = cfg_manager.get_system_config().top_layer
        builders = LayerHub.builders
        if top not in builders:
            raise ValueError(f"Unknown top layer: {top}")

        top_builder = builders.get(top)
        top_layer = top_builder(cfg_manager)
        return top_layer
