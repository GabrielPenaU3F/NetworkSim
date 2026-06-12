class ProtocolError(Exception):

    def __init__(self, message):
        super().__init__(message)


class LinkError(Exception):

    def __init__(self, message, retries=0):
        super().__init__(message)
        self.retries = retries


class NetworkError(Exception):

    def __init__(self, message):
        super().__init__(message)


class AddressError(Exception):

    def __init__(self, message):
        super().__init__(message)
