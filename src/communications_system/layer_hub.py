from src.link_layer.link import Link
from src.physical_layer.codes.physical_layer import PhysicalLayer


class LayerHub:

    @staticmethod
    def build_physical_layer(config):
        cfg = config.get_physical_layer_configs()

        # Channel
        channel_cfg = cfg['channel']
        channel = channel_cfg['class'](**channel_cfg['params'])

        # Channel code (encoder/decoder)
        code_cfg = cfg['channel_code']
        channel_code = code_cfg['class'](**code_cfg['params'])

        # Physical layer
        return PhysicalLayer(
            channel=channel,
            channel_code=channel_code
        )

    @staticmethod
    def build_link_layer(config, lower):
        cfg = config.get_link_layer_configs()

        # Checksum
        checksum_cfg = cfg['checksum']
        checksum = checksum_cfg['class'](**checksum_cfg['params'])

        # Link layer
        return Link(
            lower,
            checksum,
            cfg['block_size'],
            cfg['max_retries']
        )

    order = ['physical', 'link']
    builders = {'physical': build_physical_layer,
                'link': build_link_layer,}