import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

from infrastructure.nodes.node import Node


class Switch(Node):

    def __init__(self, link_module):
        super().__init__(address=None)
        self.link_module = link_module
        self._mac_table = {}
        self._rx_buffers = {} # one buffer per interface

    def add_interface(self, interface, edge=None):
        super().add_interface(interface, edge)
        self._rx_buffers[interface] = []

    def on_receive(self, bits, interface=None):
        buffer = self._rx_buffers[interface]
        buffer.extend(bits)

        while True:
            frame_size = self.link_module.peek_next_frame_size(buffer)
            if frame_size is None or len(buffer) < frame_size:
                break # if frame is incomplete

            frame_bits = np.array(buffer[:frame_size], dtype=np.uint8)
            buffer = self._remove_bits_from_stream_buffer(buffer, frame_size, interface)

            if not self.link_module.validate_checksum(frame_bits):
                logger.debug("Checksum error → dropping frame")
                continue

            wire_payload_size = frame_size - self.link_module.header_size - self.link_module.checksum_size
            frame = self.link_module.deserialize_frame(frame_bits, wire_payload_size)

            self._learn(frame.src_mac, interface)
            self._forward(frame_bits, frame.dst_mac, incoming_interface=interface)

        return None

    def _remove_bits_from_stream_buffer(self, buffer, frame_size, interface: int) -> Any:
        self._rx_buffers[interface] = buffer[frame_size:]
        buffer = self._rx_buffers[interface]
        return buffer

    def _learn(self, src_mac, interface):
        self._mac_table[src_mac] = interface

    def _forward(self, raw_bits, dst_mac, incoming_interface):
        target_interface = self._mac_table.get(dst_mac)

        if target_interface is not None:
            target_interface.send(raw_bits)
        else:
            self._flood(raw_bits, incoming_interface)

    def _flood(self, raw_bits, incoming_interface):
        for interface in self.interfaces:
            if interface != incoming_interface:
                interface.send(raw_bits)