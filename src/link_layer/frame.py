class Frame:

    def __init__(self, payload, seq, checksum):
        self.payload = payload
        self.seq = seq
        self.checksum = checksum

    def get_payload(self):
        return self.payload

    def get_seq(self):
        return self.seq

    def get_checksum(self):
        return self.checksum