import pytest

from src.errors import NetworkError
from src.infrastructure.network import Network
from src.system_configurations.config_manager import ConfigManager


def test_cannot_create_network_without_network_protocol():
    with pytest.raises(NetworkError) as e:
        cfg_manager = ConfigManager(top_layer='link')
        Network(cfg_manager)
        assert e.message == 'Top layer should be at least Network Layer'