import numpy as np
import pytest

from src.infrastructure.alphabets import AlphabetProvider
from src.infrastructure.sources import UniformIIDSource, ZipfIIDSource, MarkovSource, BurstySource


@pytest.fixture
def alphabet():
    return AlphabetProvider.provide_alphabet('test_16bits_alph')


class TestUniformIIDSource:

    def test_length(self, alphabet):
        np.random.seed(0)
        src = UniformIIDSource(alphabet)

        seq = src.generate(1000)
        assert len(seq) == 1000

    def test_uniform_distribution(self, alphabet):
        np.random.seed(0)
        src = UniformIIDSource(alphabet)

        n = 10000
        seq = src.generate(n)

        counts = {word: 0 for word in alphabet}
        for s in seq:
            counts[s] += 1

        expected = n / len(alphabet)

        for c in counts.values():
            assert abs(c - expected) < 0.1 * expected  # 10% tolerance

class TestZipfIIDSource:

    def test_length(self, alphabet):
        np.random.seed(0)
        src = ZipfIIDSource(alphabet)

        seq = src.generate(1000)
        assert len(seq) == 1000

    def test_zipf_not_uniform(self, alphabet):
        np.random.seed(0)
        src = ZipfIIDSource(alphabet, alpha=1.5)

        n = 20000
        seq = src.generate(n)

        counts = {word: 0 for word in alphabet}
        for s in seq:
            counts[s] += 1

        values = list(counts.values())

        assert max(values) > 2 * min(values)


class TestMarkovSource:

    def test_length(self, alphabet):
        np.random.seed(0)

        L = len(alphabet)
        P = np.ones((L, L)) / L  # transición uniforme

        src = MarkovSource(alphabet, P)
        seq = src.generate(1000)

        assert len(seq) == 1000

    def test_has_memory(self, alphabet):
        np.random.seed(0)

        L = len(alphabet)

        # matrix with a high correlation level
        P = np.eye(L) * 0.9 + (1 - 0.9) / L

        src = MarkovSource(alphabet, P)
        seq = src.generate(5000)

        same = 0
        for i in range(len(seq) - 1):
            if seq[i] == seq[i+1]:
                same += 1

        ratio = same / len(seq)

        assert ratio > 0.5  # Should repeat a lot - may fail, but with low probability


class TestBurstySource:

    def test_length(self, alphabet):
        np.random.seed(0)

        src = BurstySource(alphabet, n_bursty=2)
        seq = src.generate(1000)

        assert len(seq) == 1000

    def test_has_bursts(self, alphabet):
        np.random.seed(0)

        src = BurstySource(alphabet, n_bursty=1, p_enter=0.2, p_exit=0.1)

        seq = src.generate(5000)

        max_run = 1
        current_run = 1

        for i in range(1, len(seq)):
            if seq[i] == seq[i-1]:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1

        assert max_run > 5  # must have some long runs
