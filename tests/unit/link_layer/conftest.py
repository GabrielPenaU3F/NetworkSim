import numpy as np
import pytest

from link_layer.link_module import LinkModule
from protocol_constants import ethernet
from src.link_layer.link_layer import LinkLayer
from src.link_layer.ether_frame import EthernetFrame
from tests.utilities.dummies import DummyLowerLayer, DummyChecksum


@pytest.fixture
def example_link_module():
    return LinkModule(DummyChecksum(),
                      min_payload_bits=8,
                      max_payload_bits=16,
                      mac_size=48,
                      ether_type_size=16,
                      real_length_size=8,
                      checksum_size=1)

@pytest.fixture
def example_link_layer():
    dummy_physical = DummyLowerLayer()
    link_layer = LinkLayer(DummyChecksum(),
                           min_payload_bits=8,
                           max_payload_bits=16,
                           mac_size=48,
                           ether_type_size=16,
                           real_length_size=8,
                           checksum_size=1)
    link_layer.attach_lower(dummy_physical)
    return link_layer

@pytest.fixture
def frame_header():
    return ('02:00:00:00:00:01',
            '02:00:00:00:00:02',
            ethernet.IPV4)  # src_mac, dst_mac, ether_type

@pytest.fixture
def make_frame():
    def _make(payload, src_mac='02:00:00:00:00:01', dst_mac='02:00:00:00:00:02',
              ether_type=ethernet.IPV4, real_length=None):
        payload = np.array(payload, dtype=np.uint8)
        if real_length is None:
            real_length = len(payload)
        return EthernetFrame(
            src_mac=src_mac, dst_mac=dst_mac, ether_type=ether_type,
            real_length=real_length, checksum_algorithm=DummyChecksum(), payload=payload
        )
    return _make