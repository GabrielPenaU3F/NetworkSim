from abc import ABC, abstractmethod

import numpy as np


class Source(ABC):

    def __init__(self, alphabet):
        np.random.shuffle(alphabet)
        self.alphabet = np.array(alphabet)

    @abstractmethod
    def generate(self, n):
        pass


class UniformIIDSource(Source):

    def generate(self, n):
        return np.random.choice(self.alphabet, n)


class ZipfIIDSource(Source): # Pareto-like distribution (heavy tailed)

    def __init__(self, alphabet, alpha=1.5):
        super().__init__(alphabet)
        ranks = np.arange(1, len(alphabet) + 1)
        probs = 1 / (ranks ** alpha)
        self.probs = probs / probs.sum()

    def generate(self, n):
        return list(np.random.choice(self.alphabet, size=n, p=self.probs))

class MarkovSource(Source):

    def __init__(self, alphabet, transition_matrix):
        super().__init__(alphabet)
        self.P = transition_matrix
        self.index = {word: i for i, word in enumerate(alphabet)}

    def generate(self, n):
        state = np.random.choice(self.alphabet)
        seq = [state]

        for _ in range(n - 1):
            i = self.index[state]
            probs = self.P[i]
            state = np.random.choice(self.alphabet, p=probs)
            seq.append(state)

        return seq


class BurstySource(Source):

    def __init__(self, alphabet, n_bursty=1, p_enter=0.05, p_exit=0.2):
        super().__init__(alphabet)
        self.p_enter = p_enter
        self.p_exit = p_exit

        # Choose bursty subset
        self.bursty_symbols = np.random.choice(alphabet, n_bursty)

    def generate(self, n):
        seq = []
        in_burst = False
        current_symbol = None

        for _ in range(n):
            if in_burst:
                seq.append(current_symbol)

                if np.random.random() < self.p_exit:
                    in_burst = False
            else:
                # Choose base symbol
                symbol = np.random.choice(self.alphabet)

                # If the symbol is bursty, goto burst mode
                if symbol in self.bursty_symbols and np.random.random() < self.p_enter:
                    in_burst = True
                    current_symbol = symbol
                    seq.append(symbol)
                else:
                    seq.append(symbol)

        return seq