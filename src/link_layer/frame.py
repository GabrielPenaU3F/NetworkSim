class Frame:

    def __init__(self, seq, is_last, is_ack, real_length, payload, checksum):
        self.seq = seq
        self.is_last = is_last
        self.is_ack = is_ack
        self.real_length = real_length
        self.payload = payload
        self.checksum = checksum

    def get_payload(self):
        return self.payload

    def get_seq(self):
        return self.seq

    def get_checksum(self):
        return self.checksum

    def get_is_last(self):
        return self.is_last

    def get_is_ack(self):
        return self.is_ack

    def get_real_length(self):
        return self.real_length

    def get_true_payload(self):
        return self.payload[:self.real_length]
