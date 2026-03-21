from src.physical_layer.channels import BinarySymmetricChannel
from src.physical_layer.codes.channel_codes import NoChannelCode
from test_codebook_settings import make_test_codebook

codebook = make_test_codebook(code='basic')

channel_code = NoChannelCode()
simple_channel = BinarySymmetricChannel(channel_code, probability=0.1)
hamming_channel = BinarySymmetricChannel(channel_code, probability=0.1)

msg = "sol mar luz bosque"
msg_simple = simple_channel.transmit(codebook, msg)
msg_hamming = hamming_channel.transmit(codebook, msg)

print(f'Original message: {msg}')
print(f'Transmitted message (no channel code): {msg_simple}')
print(f'Transmitted message (Hamming code): {msg_hamming}')
