class ProtocolError(Exception):

    def __init__(self, message):
        super().__init__(message)


class LinkError(Exception):

    def __init__(self, message, retries):
        super().__init__(message)
        self.retries = retries


class NetworkError(Exception):

    def __init__(self, message):
        super().__init__(message)
