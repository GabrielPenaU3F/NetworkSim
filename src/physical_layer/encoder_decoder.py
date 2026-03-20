class EncoderDecoder:

    def __init__(self, codebook):
        self.codebook = codebook

    def encode_message(self, message):
        split_msg = message.split(' ')
        bits = ''.join(self.codebook.get_codebook()[word] for word in split_msg)
        return self.codebook.encode_bits(bits)

    def decode_message(self, bits):
        bits = self.codebook.decode_bits(bits)
        len_word = self.codebook.get_word_length()
        words = []
        for i in range(0, len(bits), len_word):
            word_bits = bits[i:i+len_word]
            word = self.codebook.get_reverse_codebook().get(word_bits, '???')
            words.append(word)
        return ' '.join(words)