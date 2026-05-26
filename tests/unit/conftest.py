import pytest

from src.infrastructure.network import Network
from src.system_configurations.config_manager import ConfigManager


@pytest.fixture
def simple_network():
    return Network(ConfigManager(top_layer='network'))