import pytest

from src.infrastructure.network import Network
from src.system_configurations.config_manager import ConfigManager


@pytest.fixture
def basic_network():
    return Network(ConfigManager())