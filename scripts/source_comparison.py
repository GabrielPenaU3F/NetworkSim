from collections import Counter

import numpy as np
from matplotlib import pyplot as plt

from src.infrastructure.alphabets import AlphabetProvider
from src.infrastructure.sources import UniformIIDSource, MarkovSource, BurstySource, ZipfIIDSource


def generate_markov_transition_matrix():
    X = np.random.gamma(1, 2, size=(L, L))

    # Calculate the sum of each row
    row_sums = X.sum(axis=1, keepdims=True)

    # Handle rows that sum to zero to avoid division by zero errors
    # In this example, we replace zero sums with 1 (or another non-zero value)
    row_sums[row_sums == 0] = 1
    return X / row_sums

def plot_histogram(sequence, alphabet, title="Histogram"):
    counts = Counter(sequence)
    values = [counts[a] for a in alphabet]

    plt.figure()
    plt.bar(alphabet, values)
    plt.xticks(rotation=90)
    plt.title(title)
    plt.tight_layout()
    plt.show()

def compute_entropy(sequence, alphabet):
    counts = Counter(sequence)
    total = len(sequence)
    probs = np.array([counts[a]/total for a in alphabet if counts[a] > 0])
    return -np.sum(probs * np.log2(probs))

def print_stats(sequence, alphabet, name="Source"):
    counts = Counter(sequence)

    print(f"\n{name}")
    print(f"Length: {len(sequence)}")
    print(f"Unique symbols: {len(counts)}")

    H = compute_entropy(sequence, alphabet)
    print(f"Empirical entropy: {H:.4f}")

    print("Top 5 most common:")
    for word, c in counts.most_common(5):
        print(f"  {word}: {c}")


alphabet = AlphabetProvider.provide_alphabet('test_16bits_alph')
L = len(alphabet)
markov_transition = generate_markov_transition_matrix()

src1 = UniformIIDSource(alphabet) # Entropy H = log2(16) = 4
src2 = MarkovSource(alphabet, markov_transition) # Entropy near 4 (near uniform)
src3 = ZipfIIDSource(alphabet) # Entropy less than 4 (heavy-tailed)
src4 = BurstySource(alphabet, p_enter=0.4, p_exit=0.02) # Entropy << 4 (not nearly uniform)

n = 2000
seq1 = src1.generate(n)
seq2 = src2.generate(n)
seq3 = src3.generate(n)
seq4 = src4.generate(n)

plot_histogram(seq1, alphabet, "Random")
plot_histogram(seq2, alphabet, "Markov")
plot_histogram(seq3, alphabet, "Zipf")
plot_histogram(seq4, alphabet, "Bursty")

print_stats(seq1, alphabet, "Random")
print_stats(seq2, alphabet, "Markov")
print_stats(seq3, alphabet, "Zipf")
print_stats(seq4, alphabet, "Bursty")
