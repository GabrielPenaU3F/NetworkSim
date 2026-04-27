class Frame:

    def __init__(self, payload, seq, checksum, is_last=0):
        self.payload = payload
        self.seq = seq
        self.checksum = checksum
        self.is_last = is_last

    def get_payload(self):
        return self.payload

    def get_seq(self):
        return self.seq

    def get_checksum(self):
        return self.checksum

    def get_is_last(self):
        return self.is_last
