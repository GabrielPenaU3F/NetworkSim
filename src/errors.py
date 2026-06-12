class ProtocolError(Exception):
    """Raised when the protocol stack is misconfigured or used incorrectly."""


class LinkError(Exception):
    """Raised when the link layer exceeds its retry budget while transmitting a frame."""

    def __init__(self, message, retries=0):
        super().__init__(message)
        self.retries = retries


class NetworkError(Exception):
    """Raised for invalid network-level operations (routing, topology, connectivity)."""


class AddressError(Exception):
    """Raised when an address is malformed, missing, or already in use."""
