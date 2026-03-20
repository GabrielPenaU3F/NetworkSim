from src.physical_layer.channels import BinarySymmetricChannel
from test_codebook_settings import make_test_codebook

cb_basic = make_test_codebook(code='basic')
cb_rep = make_test_codebook(code='repetition')

channel = BinarySymmetricChannel(0.1)

msg = "sol mar luz bosque"

print(f'Original message: {msg}')
print(f'With basic code: {channel.transmit(cb_basic, msg)}')
print(f'With repetition code: {channel.transmit(cb_rep, msg)}')
