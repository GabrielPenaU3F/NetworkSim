import numpy as np
from matplotlib import pyplot as plt

from alphabets.alphabets import AlphabetProvider
from src.physical_layer.sources import UniformIIDSource, ZipfIIDSource
from src.physical_layer.utils import estimate_aep

def plot_aep(curve, true_entropy=None, title="AEP convergence"):
    plt.figure()
    plt.plot(curve, label="Empirical", color='red')

    if true_entropy is not None:
        plt.axhline(true_entropy, linestyle='--', label="True H")

    plt.xlabel("n")
    plt.ylabel("-1/n log P(X^n)")
    plt.title(title)
    plt.legend()
    plt.show()

alphabet = AlphabetProvider.provide_alphabet('test_16bits_alph')

src = ZipfIIDSource(alphabet)

seq = src.generate(5000)
probs = src.get_probs()

curve = estimate_aep(seq, probs)

H = -sum(p * np.log2(p) for p in probs.values())

plot_aep(curve, H, title="AEP - IID Source")