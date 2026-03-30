import numpy as np

def str_to_bits(string, dtype=np.uint8):
    return np.fromiter((int(c) for c in string), dtype=dtype)

def bits_to_str(bits):
    return ''.join(str(int(b)) for b in bits)

def int_to_bits(value, num_bits):
    return np.array(
        [(value >> i) & 1 for i in reversed(range(num_bits))],
        dtype=np.uint8
    )

def bits_to_int(bits):
    n = len(bits)
    return np.sum([bits[k] * np.pow(2, n - k) for k in range(n)])

def select_binary_format(alphabet):
    n = len(alphabet)
    n_bits = int(np.ceil(np.log2(n)))
    return f'0{n_bits}b'
