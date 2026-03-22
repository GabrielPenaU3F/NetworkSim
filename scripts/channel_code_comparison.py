from src.physical_layer.channels import BinarySymmetricChannel
from src.physical_layer.codes.channel_codes import NoChannelCode, RepetitionChannelCode

no_channel_code = NoChannelCode()
repetition_channel_code = RepetitionChannelCode(r=3)

simple_channel = BinarySymmetricChannel(no_channel_code, probability=0.1)
repetition_channel = BinarySymmetricChannel(repetition_channel_code, probability=0.1)

msg = "1100111100000011"
msg_simple = simple_channel.transmit(msg)
msg_repetition = repetition_channel.transmit(msg)

print(f'Original message: {msg}')
print(f'Transmitted message (no channel code): {msg_simple}')
print(f'Transmitted message (Repetition code): {msg_repetition}')
