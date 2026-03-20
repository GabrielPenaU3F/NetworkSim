# Test alphabet
from src.physical_layer.channels import BinarySymmetricChannel
from test_codebook_settings import make_test_codebook

codebook = make_test_codebook()
channel = BinarySymmetricChannel(0.1)
message = 'sombra luz'

received = channel.transmit(codebook, message)
print(received)
