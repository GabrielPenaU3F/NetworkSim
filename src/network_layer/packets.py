from src.errors import NetworkError


class IPPacket:

    def __init__(self, origin_address, destination_address, payload):
        if origin_address is None or destination_address is None:
            raise NetworkError('Origin and Destination addresses must be specified')
        self.origin_address = origin_address
        self.destination_address = destination_address
        self.payload = payload
