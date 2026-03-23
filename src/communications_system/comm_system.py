from src.communications_system.layer_hub import LayerHub


class CommSystem:

    def __init__(self, config):
        self.stack = self.build_stack(config)

    def transmit(self, codebook, message):

        # Source encoding
        source_bits = codebook.encode_message(message)

        # Transmission
        received_bits = self.stack.transmit(source_bits)

        # Source decoding
        message = codebook.decode_message(received_bits)
        return message

    def build_stack(self, config):
        top = config.get_system_configs().get('top_layer')
        order = LayerHub.order
        builders = LayerHub.builders
        if top not in order:
            raise ValueError(f"Unknown top layer: {top}")

        layers_to_build = order[:order.index(top) + 1]
        lower = None
        for layer_name in layers_to_build:
            builder = builders.get(layer_name)

            if lower is None: # The physical layer receives only the configuration file
                lower = builder(config)
            else: # Each higher layer receives its immediate bottom one
                lower = builder(config, lower)

        # At this step, the variable 'lower' contains the highest layer
        return lower
