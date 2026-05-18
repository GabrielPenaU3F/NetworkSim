import pytest

from src.link_layer.link_layer import LinkLayer
from src.physical_layer.physical_layer import PhysicalLayer
from src.protocol_stack.protocol_stack import ProtocolStack
from src.system_configurations.config_manager import ConfigManager

@pytest.fixture
def physical_stack():
    cfg = ConfigManager(top_layer='physical')
    return ProtocolStack(cfg)

class TestProtocolStackPhysicalLayer:

    def test_top_layer_is_physical(self, physical_stack):
        assert type(physical_stack.top_layer) is PhysicalLayer

    def test_bottom_layer_is_physical(self, physical_stack):
        assert type(physical_stack.bottom_layer) is PhysicalLayer

class TestProtocolStackLinkLayer:

    def test_top_layer_is_link(self, link_stack):
        assert type(link_stack.top_layer) is LinkLayer

    def test_bottom_layer_is_physical(self, link_stack):
        assert type(link_stack.bottom_layer) is PhysicalLayer

    def test_physical_and_link_layer_are_connected_in_correct_order(self, link_stack):
        physical_layer = link_stack.bottom_layer
        link_layer = link_stack.top_layer
        assert type(physical_layer.upper_layer) is LinkLayer
        assert type(link_layer.lower_layer) is PhysicalLayer

    def test_stack_extremes_are_correct(self, link_stack):
        physical_layer = link_stack.bottom_layer
        link_layer = link_stack.top_layer
        assert physical_layer.lower_layer is None
        assert link_layer.upper_layer is None
