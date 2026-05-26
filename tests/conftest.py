import numpy as np
import pytest

from src.link_layer.checksum import ParityChecksum
from src.link_layer.link_layer import LinkLayer
from src.protocol_stack.protocol_stack import ProtocolStack
from src.system_configurations.config_manager import ConfigManager
from tests.utilities.dummies import DummyPhysicalLayer, CleanChannel


@pytest.fixture
def clean_channel():
    return CleanChannel()

@pytest.fixture
def tile_bits():
    def _make_tile(n):
        return np.tile([0, 1], n)
    return _make_tile

@pytest.fixture
def link_stack():
    cfg = ConfigManager(top_layer='link')
    return ProtocolStack(cfg)

@pytest.fixture
def example_link_layer():
    dummy_physical = DummyPhysicalLayer()
    checksum = ParityChecksum()
    link_layer = LinkLayer(checksum, seq_size=2, payload_size=8, checksum_size=2)
    link_layer.attach_lower(dummy_physical)
    return link_layer