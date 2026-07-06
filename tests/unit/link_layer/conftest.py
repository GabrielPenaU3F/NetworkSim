import pytest

from link_layer.ether_frame import EthernetFrame
from protocol_constants import ethernet
from src.link_layer.link_layer import LinkLayer
from tests.utilities.dummies import DummyLayer, DummyChecksum


@pytest.fixture
def example_link_layer(dummy_layer):
    link_layer = LinkLayer(DummyChecksum(),
                           min_payload_bits=8,
                           max_payload_bits=16,
                           mac_size=48,
                           ether_type_size=16,
                           real_length_size=8,
                           checksum_size=1)
    link_layer.attach_lower(dummy_layer)
    return link_layer

@pytest.fixture
def frame_header():
    return ('02:00:00:00:00:01',
            '02:00:00:00:00:02',
            ethernet.IPV4)  # src_mac, dst_mac, ether_type


@pytest.fixture
def example_frame(tile_bits):
    return EthernetFrame(
        src_mac='02:00:00:00:00:01',
        dst_mac='02:00:00:00:00:02',
        ether_type=ethernet.IPV4,
        real_length=8,
        payload=tile_bits(4),  # 8 bits
        checksum=1,
    )

@pytest.fixture
def frame_to_deserialize(example_link_module, example_frame):
    return example_link_module.serialize_frame(example_frame)