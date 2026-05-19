from abc import ABC, abstractmethod

import numpy as np


class Source(ABC):

    probs = None

    def __init__(self, alphabet, source_rng=None):
        self.alphabet = alphabet
        self.source_rng = source_rng if source_rng is not None else np.random.default_rng(seed=0)

        self.source_rng.shuffle(self.alphabet)

    @abstractmethod
    def generate(self, n):
        pass


class UniformIIDSource(Source):

    def __init__(self, alphabet, source_rng=None):
        super().__init__(alphabet, source_rng)
        L = len(alphabet)
        self.probs = np.ones(L) / L

    def generate(self, n):
        return self.source_rng.choice(self.alphabet, n)

    def get_probs(self):
        return dict(zip(self.alphabet, self.probs))


class ZipfIIDSource(Source): # Pareto-like distribution (heavy tailed)

    def __init__(self, alphabet, alpha=1.5, source_rng=None):
        super().__init__(alphabet, source_rng)
        ranks = np.arange(1, len(alphabet) + 1)
        probs = 1 / (ranks ** alpha)
        self.probs = probs / probs.sum()

    def generate(self, n):
        return list(self.source_rng.choice(self.alphabet, size=n, p=self.probs))

    def get_probs(self):
        return dict(zip(self.alphabet, self.probs))

class MarkovSource(Source):

    def __init__(self, alphabet, transition_matrix, source_rng=None):
        super().__init__(alphabet, source_rng)
        self.P = transition_matrix
        self.index = {word: i for i, word in enumerate(alphabet)}

    def generate(self, n):
        state = self.source_rng.choice(self.alphabet)
        seq = [state]

        for _ in range(n - 1):
            i = self.index[state]
            probs = self.P[i]
            state = self.source_rng.choice(self.alphabet, p=probs)
            seq.append(state)

        return seq


class BurstySource(Source):

    def __init__(self, alphabet, n_bursty=1, p_enter=0.05, p_exit=0.2, source_rng=None):
        super().__init__(alphabet, source_rng)
        self.p_enter = p_enter
        self.p_exit = p_exit

        # Choose bursty subset
        self.bursty_symbols = self.source_rng.choice(alphabet, n_bursty)

    def generate(self, n):
        seq = []
        in_burst = False
        current_symbol = None

        for _ in range(n):
            if in_burst:
                seq.append(current_symbol)

                if self.source_rng.random() < self.p_exit:
                    in_burst = False
            else:
                # Choose base symbol
                symbol = self.source_rng.choice(self.alphabet)

                # If the symbol is bursty, goto burst mode
                if symbol in self.bursty_symbols and self.source_rng.random() < self.p_enter:
                    in_burst = True
                    current_symbol = symbol
                    seq.append(symbol)
                else:
                    seq.append(symbol)

        return seq
