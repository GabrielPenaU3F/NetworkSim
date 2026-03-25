from src.physical_layer.codes.source_codes import BasicSourceCode
from src.physical_layer.utils import str_to_bits, bits_to_str


class Codebook:

    # These must be source codes
    available_codes = {
        'basic': BasicSourceCode,
    }
    alphabet = []
    codebook = []
    reverse_codebook = []

    def __init__(self, alphabet, code='basic'):
        self.alphabet = alphabet
        self.code = self.available_codes[code]()
        self.codebook, self.reverse_codebook = self.code.build_codebook(alphabet)
        self.word_length = len(next(iter(self.codebook.values()))) # Valid only if every codeword has the same length

    def print_codebook(self):
        print('Word -- Code')
        print([f'{word}: {self.codebook[word]}' for word in self.alphabet])

    def encode_message(self, message):
        split_msg = message.split(' ')
        bits = ''.join(self.codebook[word] for word in split_msg)
        encoded_bits = self.code.encode_bits(bits)
        return str_to_bits(encoded_bits)

    def decode_message(self, message):
        bits = bits_to_str(message)
        bits = self.code.decode_bits(bits)
        len_word = self.word_length
        words = []
        for i in range(0, len(bits), len_word):
            word_bits = bits[i:i+len_word]
            word = self.reverse_codebook.get(word_bits, '???')
            words.append(word)
        return ' '.join(words)
