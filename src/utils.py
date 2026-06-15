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
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return value

def pad_bits(bits, size):
    padding = (size - len(bits) % size) % size
    return np.concatenate([bits, np.zeros(padding, dtype=np.uint8)]), padding

def unpad_bits(bits, padding):
    if padding == 0:
        return bits
    return bits[:-padding]

def select_binary_format(alphabet):
    n = len(alphabet)
    n_bits = int(np.ceil(np.log2(n)))
    return f'0{n_bits}b'

def serialize_ip_address(address: str, num_bits: int = 32) -> np.ndarray:
    parts = address.split('.')
    num_parts = len(parts)

    if num_bits < num_parts * 8:
        raise ValueError(f'{num_bits} bits are not enough to represent {num_parts} parts of 8 bits each')

    values = [int(p) for p in parts]

    if not all(0 <= v <= 255 for v in values):
        raise ValueError('Each part must be between 0 and 255')

    int_value = 0
    for v in values:
        int_value = (int_value << 8) | v

    return int_to_bits(int_value, num_bits)


def deserialize_ip_address(bits: np.ndarray, num_parts: int = 4) -> str:
    if len(bits) < num_parts * 8:
        raise ValueError(f'{len(bits)} bits are not enough to deserialize {num_parts} parts of 8 bits each')

    int_value = bits_to_int(bits)

    parts = []
    for _ in range(num_parts):
        parts.append(int_value & 0xFF)
        int_value >>= 8

    return '.'.join(str(p) for p in reversed(parts))

def serialize_mac_address(mac: str, num_bits: int = 48) -> np.ndarray:
    parts = mac.split(':')
    num_parts = len(parts)

    if num_bits < num_parts * 8:
        raise ValueError(f'{num_bits} bits are not enough to represent {num_parts} parts of 8 bits each')

    values = [int(p, 16) for p in parts]

    int_value = 0
    for v in values:
        int_value = (int_value << 8) | v

    return int_to_bits(int_value, num_bits)

def deserialize_mac_address(bits: np.ndarray, num_parts: int = 6) -> str:
    if len(bits) < num_parts * 8:
        raise ValueError(f'{len(bits)} bits are not enough to deserialize {num_parts} parts of 8 bits each')

    int_value = bits_to_int(bits)

    parts = []
    for _ in range(num_parts):
        parts.append(int_value & 0xFF)
        int_value >>= 8

    return ':'.join(f'{p:02x}' for p in reversed(parts))