# Test alphabet
from src.physical_layer.channels import BinarySymmetricChannel
from src.physical_layer.codes.channel_codes import NoChannelCode
from test_codebook_settings import make_test_codebook

codebook = make_test_codebook()
channel = BinarySymmetricChannel(NoChannelCode(), 0.1)
message = '1101'

received = channel.transmit(codebook, message)
print(received)
