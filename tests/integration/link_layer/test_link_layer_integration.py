from protocol_constants import ethernet


def test_interface_is_propagated_upward_on_receive(example_link_layer, dummy_layer, dummy_interface, tile_bits):
    example_link_layer.upper_layer = dummy_layer

    bits = tile_bits(4)
    frames = example_link_layer._build_frames(bits,
                                              src_mac='02:00:00:00:00:01',
                                              dst_mac='02:00:00:00:00:02',
                                              ether_type=ethernet.IPV4)
    for frame in frames:
        serialized = example_link_layer._link_module.serialize_frame(frame)
        example_link_layer.on_receive(serialized, interface=dummy_interface)

    assert dummy_layer.received_interface == dummy_interface