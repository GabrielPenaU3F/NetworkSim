class Frame:

    def __init__(self, seq, is_last, real_length, payload, checksum):
        self.payload = payload
        self.real_length = real_length
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

    def get_real_length(self):
        return self.real_length
