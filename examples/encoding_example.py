# Test alphabet
from src.physical_layer.encoder_decoder import EncoderDecoder
from test_codebook_settings import make_test_codebook

codebook = make_test_codebook(code='repetition')
ed = EncoderDecoder(codebook)
encoded_msg = ed.encode_message('sombra luz')
print(encoded_msg)

decoded_msg = ed.decode_message(encoded_msg)
print(decoded_msg)
