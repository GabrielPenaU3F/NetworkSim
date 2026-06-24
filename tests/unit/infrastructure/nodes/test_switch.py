import numpy as np
import pytest

from infrastructure.nodes.switch import Switch
from protocol_constants import ethernet
from system_configurations.config import EthernetLinkConfig, ChecksumConfig
from system_configurations.config_manager import ConfigManager
from tests.utilities.dummies import DummyInterface, DummyChecksum



@pytest.fixture
def switch(example_link_module):
    cfg_manager = ConfigManager(link=EthernetLinkConfig(checksum_cfg=ChecksumConfig(cls=DummyChecksum),
                                                        min_payload_bits=8,
                                                        max_payload_bits=16,
                                                        mac_size=48,
                                                        ether_type_size=16,
                                                        real_length_size=8,
                                                        checksum_size=1)
                                )
    return Switch(cfg_manager)

@pytest.fixture
def make_interface():
    def _make(mac):
        iface = DummyInterface()
        iface.mac_address = mac
        return iface
    return _make

@pytest.fixture
def frame_bits(example_link_module, tile_bits):
    def _make(src_mac, dst_mac, ether_type=ethernet.IPV4, payload=None):
        if payload is None:
            payload = tile_bits(4)  # 8 bits, exact minimum
        frame = example_link_module.build_frame(src_mac, dst_mac, ether_type, real_length=len(payload), payload=payload)
        return example_link_module.serialize_frame(frame)
    return _make


class TestInterfaceManagement:

    def test_adding_interface_initializes_its_buffer(self, switch, make_interface):
        iface = make_interface('02:00:00:00:00:01')
        switch.add_interface(iface)
        assert switch._rx_buffers[iface] == []

    def test_switch_can_have_multiple_interfaces(self, switch, make_interface):
        iface_a = make_interface('02:00:00:00:00:01')
        iface_b = make_interface('02:00:00:00:00:02')
        switch.add_interface(iface_a)
        switch.add_interface(iface_b)
        assert len(switch.interfaces) == 2


class TestMACLearning:

    def test_switch_learns_source_mac_on_receive(self, switch, make_interface, frame_bits):
        iface_in = make_interface('02:00:00:00:00:01')
        iface_out = make_interface('02:00:00:00:00:02')
        switch.add_interface(iface_in)
        switch.add_interface(iface_out)

        bits = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:0b')
        switch.on_receive(bits, interface=iface_in)

        assert switch._mac_table['02:00:00:00:00:0a'] == iface_in

    def test_switch_updates_mac_table_if_source_moves(self, switch, make_interface, frame_bits):
        iface_a = make_interface('02:00:00:00:00:01')
        iface_b = make_interface('02:00:00:00:00:02')
        switch.add_interface(iface_a)
        switch.add_interface(iface_b)

        bits = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:0b')
        switch.on_receive(bits, interface=iface_a)
        switch.on_receive(bits, interface=iface_b)

        assert switch._mac_table['02:00:00:00:00:0a'] == iface_b


class TestFlooding:

    def test_unknown_destination_is_flooded_to_all_other_interfaces(self, switch, make_interface, frame_bits):
        iface_in = make_interface('02:00:00:00:00:01')
        iface_b = make_interface('02:00:00:00:00:02')
        iface_c = make_interface('02:00:00:00:00:03')
        switch.add_interface(iface_in)
        switch.add_interface(iface_b)
        switch.add_interface(iface_c)

        bits = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:ff')
        switch.on_receive(bits, interface=iface_in)

        assert iface_b.last_sent_bits is not None
        assert iface_c.last_sent_bits is not None

    def test_flooding_does_not_send_back_to_incoming_interface(self, switch, make_interface, frame_bits):
        iface_in = make_interface('02:00:00:00:00:01')
        iface_b = make_interface('02:00:00:00:00:02')
        switch.add_interface(iface_in)
        switch.add_interface(iface_b)

        bits = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:ff')
        switch.on_receive(bits, interface=iface_in)

        assert iface_in.last_sent_bits is None


class TestForwarding:

    def test_known_destination_is_forwarded_only_to_correct_interface(self, switch, make_interface, frame_bits):
        iface_a = make_interface('02:00:00:00:00:01')
        iface_b = make_interface('02:00:00:00:00:02')
        iface_c = make_interface('02:00:00:00:00:03')
        switch.add_interface(iface_a)
        switch.add_interface(iface_b)
        switch.add_interface(iface_c)

        # B announces itself first, so the switch learns B is behind iface_b
        announce_bits = frame_bits(src_mac='02:00:00:00:00:0b', dst_mac='02:00:00:00:00:0a')
        switch.on_receive(announce_bits, interface=iface_b)
        iface_c.last_sent_bits = None # Make it forget the flood

        # Now A sends a frame addressed to B
        data_bits = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:0b')
        switch.on_receive(data_bits, interface=iface_a)

        assert iface_b.last_sent_bits is not None
        assert iface_c.last_sent_bits is None # C should still be None

    def test_forwarded_bits_are_unchanged(self, switch, make_interface, frame_bits):
        iface_a = make_interface('02:00:00:00:00:01')
        iface_b = make_interface('02:00:00:00:00:02')
        switch.add_interface(iface_a)
        switch.add_interface(iface_b)

        announce_bits = frame_bits(src_mac='02:00:00:00:00:0b', dst_mac='02:00:00:00:00:0a')
        switch.on_receive(announce_bits, interface=iface_b)

        data_bits = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:0b')
        switch.on_receive(data_bits, interface=iface_a)

        assert np.all(iface_b.last_sent_bits == data_bits)


class TestChecksumValidation:

    def test_corrupted_frame_is_dropped_and_not_forwarded(self, switch, make_interface, frame_bits):
        iface_a = make_interface('02:00:00:00:00:01')
        iface_b = make_interface('02:00:00:00:00:02')
        switch.add_interface(iface_a)
        switch.add_interface(iface_b)

        bits = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:0b').copy()
        bits[0] ^= 1  # corrupt the frame

        switch.link_module.validate_checksum = lambda x: False  # force checksum failure regardless of dummy checksum
        switch.on_receive(bits, interface=iface_a)

        assert iface_b.last_sent_bits is None

    def test_corrupted_frame_does_not_update_mac_table(self, switch, make_interface, frame_bits):
        iface_a = make_interface('02:00:00:00:00:01')
        switch.add_interface(iface_a)

        bits = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:0b')

        switch.link_module.validate_checksum = lambda x: False
        switch.on_receive(bits, interface=iface_a)

        assert '02:00:00:00:00:0a' not in switch._mac_table


class TestFragmentedReception:

    def test_frame_arriving_in_chunks_is_processed_once_complete(self, switch, make_interface, frame_bits):
        iface_a = make_interface('02:00:00:00:00:01')
        iface_b = make_interface('02:00:00:00:00:02')
        switch.add_interface(iface_a)
        switch.add_interface(iface_b)

        announce_bits = frame_bits(src_mac='02:00:00:00:00:0b', dst_mac='02:00:00:00:00:0a')
        switch.on_receive(announce_bits, interface=iface_b)

        data_bits = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:0b')
        midpoint = len(data_bits) // 2

        switch.on_receive(data_bits[:midpoint], interface=iface_a)
        assert iface_b.last_sent_bits is None  # not complete yet

        switch.on_receive(data_bits[midpoint:], interface=iface_a)
        assert iface_b.last_sent_bits is not None


class TestMultipleFramesInOneCall:

    def test_two_frames_arriving_together_are_both_forwarded(self, switch, make_interface, frame_bits):
        iface_a = make_interface('02:00:00:00:00:01')
        iface_b = make_interface('02:00:00:00:00:02')
        switch.add_interface(iface_a)
        switch.add_interface(iface_b)

        announce_bits = frame_bits(src_mac='02:00:00:00:00:0b', dst_mac='02:00:00:00:00:0a')
        switch.on_receive(announce_bits, interface=iface_b)

        frame_1 = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:0b',
                             payload=np.array([0,1,0,1,0,1,0,1], dtype=np.uint8))
        frame_2 = frame_bits(src_mac='02:00:00:00:00:0a', dst_mac='02:00:00:00:00:0b',
                             payload=np.array([1,0,1,0,1,0,1,0], dtype=np.uint8))
        combined = np.concatenate([frame_1, frame_2])

        switch.on_receive(combined, interface=iface_a)

        assert np.all(iface_b.sent_bits[-2] == frame_1)
        assert np.all(iface_b.sent_bits[-1] == frame_2)