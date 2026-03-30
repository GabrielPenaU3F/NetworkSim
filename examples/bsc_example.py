# Test alphabet
from src.physical_layer.alphabets.alphabets import AlphabetProvider
from src.physical_layer.channels import BinarySymmetricChannel
from src.physical_layer.codebook import Codebook

alphabet = AlphabetProvider.provide_alphabet('test_16bits_alph')
codebook = Codebook(alphabet)
channel = BinarySymmetricChannel(error_prob=0.1)
message = [1, 1, 0, 1]

received = channel.apply_noise(message)
print(received)
