from src.errors import NetworkError
from src.infrastructure.nodes import Host


class Network:

    _address_registry = None
    cfg_manager = None

    def __init__(self, cfg_manager):
        self.validate_config(cfg_manager)
        self.cfg_manager = cfg_manager
        self._address_registry = set()

    def create_host(self, address='192.168.0.1'):

        if address in self._address_registry:
            raise NetworkError(f'Address {address} already in use')

        host = Host(self.cfg_manager, address=address)
        self._address_registry.add(address)
        return host

    def validate_config(self, cfg_manager):
        top_layer = cfg_manager.get_protocol_stack_config().top_layer
        if top_layer in ['physical', 'link']:
            raise NetworkError('Top layer should be at least Network Layer')
