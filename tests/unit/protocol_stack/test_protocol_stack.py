import pytest

from src.link_layer.link_layer import LinkLayer
from src.physical_layer.physical_layer import PhysicalLayer
from src.protocol_stack.protocol_stack import ProtocolStack
from src.system_configurations.config_manager import ConfigManager

@pytest.fixture
def physical_stack():
    cfg = ConfigManager(top_layer='physical')
    return ProtocolStack(cfg)

class TestProtocolStack:

    def test_can_get_link_layer(self, link_stack):
        link_layer = link_stack.get_layer('link')
        assert type(link_layer) is LinkLayer
        assert link_layer == link_stack.top_layer

    def test_can_get_physical_layer(self, link_stack):
        physical_layer = link_stack.get_layer('physical')
        assert type(physical_layer) is PhysicalLayer
        assert physical_layer == link_stack.bottom_layer

    def test_cannot_get_nonexistent_layers(self, link_stack):
        with pytest.raises(KeyError, match='Unknown layer: transport'):
            link_stack.get_layer('transport')

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
