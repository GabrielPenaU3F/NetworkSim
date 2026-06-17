from copy import deepcopy

from src.system_configurations.config import PhysicalConfig, EthernetLinkConfig, InfrastructureConfig, \
    NetworkConfig


class ConfigManager:

    def __init__(self, top_layer='network',
            infrastructure: InfrastructureConfig = None,
            physical: PhysicalConfig = None,
            link: EthernetLinkConfig = None,
            network: NetworkConfig = None,
    ):

        self.top_layer = top_layer
        self.infrastructure_cfg = deepcopy(infrastructure) or InfrastructureConfig()
        self.physical_layer_cfg = deepcopy(physical) if physical else PhysicalConfig()
        self.link_layer_cfg = deepcopy(link) if link else EthernetLinkConfig()
        self.network_layer_cfg = deepcopy(network) if network else NetworkConfig()
