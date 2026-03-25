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

def hamming_distance(a, b):
    return sum(x != y for x, y in zip(a, b))

def estimate_aep(sequence, prob_dict):
    log_probs = []

    for x in sequence:
        p = prob_dict[x]
        log_probs.append(-np.log2(p))

    log_probs = np.array(log_probs)

    # promedio acumulado
    cumulative_avg = np.cumsum(log_probs) / np.arange(1, len(log_probs)+1)

    return cumulative_avg
