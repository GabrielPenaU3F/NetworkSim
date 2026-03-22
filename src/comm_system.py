from src.link_layer.link import Link
from src.physical_layer.channels import BinarySymmetricChannel


class CommSystem:

    def __init__(self, config):
        self.channel = self.build_physical_layer(config)
        self.link = self.build_link_layer(config)

    def build_physical_layer(self, config):
        physical_configs = config.get_physical_layer_configs()
        channel_code = physical_configs.get('channel_code')()
        error_prob = physical_configs.get('error_prob')
        channel = physical_configs.get('channel')(channel_code, error_prob)
        return channel

    def build_link_layer(self, config):
        link_configs = config.get_link_layer_configs()
        block_size = link_configs.get('block_size')
        max_retries = link_configs.get('max_retries')
        checksum = link_configs.get('checksum')()
        link = Link(self.channel, checksum, block_size, max_retries)
        return link

    def transmit(self, codebook, message):

        # Source encoding
        source_bits = codebook.encode_message(message)

        # Transmission

        # Link transmission
        received_bits = self.link.transmit(source_bits)

        # Source decoding
        message = codebook.decode_message(received_bits)
        return message
