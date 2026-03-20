import numpy as np

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
