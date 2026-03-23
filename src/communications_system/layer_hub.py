from src.link_layer.link import Link


class LayerHub:

    @staticmethod
    def build_physical_layer(config):
        physical_configs = config.get_physical_layer_configs()
        channel_code = physical_configs.get('channel_code')()
        error_prob = physical_configs.get('error_prob')
        channel = physical_configs.get('channel')(channel_code, error_prob)
        return channel

    @staticmethod
    def build_link_layer(config, channel):
        link_configs = config.get_link_layer_configs()
        block_size = link_configs.get('block_size')
        max_retries = link_configs.get('max_retries')
        checksum = link_configs.get('checksum')()
        link = Link(channel, checksum, block_size, max_retries)
        return link

    order = ['physical', 'link']
    builders = {'physical': build_physical_layer,
                'link': build_link_layer,}