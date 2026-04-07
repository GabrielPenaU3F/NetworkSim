# Test alphabet
from src.infrastructure.alphabets import AlphabetProvider
from src.infrastructure.channels import BinarySymmetricChannel
from src.infrastructure.codebook import Codebook

alphabet = AlphabetProvider.provide_alphabet('test_16bits_alph')
codebook = Codebook(alphabet)
channel = BinarySymmetricChannel(error_prob=0.1)
message = [1, 1, 0, 1]

received = channel.apply_noise(message)
print(received)
