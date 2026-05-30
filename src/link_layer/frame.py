class Frame:

    def __init__(self, seq, is_last, is_ack, real_length, payload, checksum):
        self.seq = seq
        self.is_last = is_last
        self.is_ack = is_ack
        self.real_length = real_length
        self.payload = payload
        self.checksum = checksum

    def get_true_payload(self):
        return self.payload[:self.real_length]
