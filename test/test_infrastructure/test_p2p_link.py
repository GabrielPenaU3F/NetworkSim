import pytest

from src.infrastructure.p2p_link import P2PLink
from src.system_configurations.config_manager import ConfigManager


@pytest.fixture
def cfg_manager():
    return ConfigManager()


# def test_p2p_send():
#     cfg_manager = ConfigManager()
#     node_a = Node("A", cfg_manager)
#     node_b = Node("B", cfg_manager)
#     P2PLink(node_a, node_b)
#     node_a.send("sol", interface=0)
#     assert node_b.last_message == "sol"
from src.infrastructure.nodes import Node


# def test_link_creates_interfaces(cfg_manager):
#     A = Node("A", cfg_manager)
#     B = Node("B", cfg_manager)
#     channel = cfg_manager.get_infrastructure_config().channel
#
#     link = P2PLink(A, B, channel)
#
#     assert len(A.interfaces) == 1
#     assert len(B.interfaces) == 1