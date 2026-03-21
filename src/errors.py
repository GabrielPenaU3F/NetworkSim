class LinkError(Exception):

    def __init__(self, message, retries):
        super().__init__(message)
        self.retries = retries
