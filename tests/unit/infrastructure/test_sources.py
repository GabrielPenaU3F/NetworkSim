import numpy as np
import pytest

from src.infrastructure.alphabets import AlphabetProvider
from src.infrastructure.sources import UniformIIDSource, ZipfIIDSource, MarkovSource, BurstySource


@pytest.fixture
def alphabet():
    return AlphabetProvider.provide_alphabet('test_16bits_alph')

@pytest.fixture
def fixed_rng():
    return np.random.default_rng(seed=0)


class TestUniformIIDSource:

    def test_length(self, alphabet, fixed_rng):
        src = UniformIIDSource(alphabet, source_rng=fixed_rng)
        seq = src.generate(1000)
        assert len(seq) == 1000

    def test_uniform_distribution(self, alphabet, fixed_rng):
        src = UniformIIDSource(alphabet, source_rng=fixed_rng)
        n = 10000
        seq = src.generate(n)

        counts = {word: 0 for word in alphabet}
        for s in seq:
            counts[s] += 1

        expected = n / len(alphabet)
        for c in counts.values():
            assert abs(c - expected) < 0.1 * expected  # 10% tolerance

class TestZipfIIDSource:

    def test_length(self, alphabet, fixed_rng):
        src = ZipfIIDSource(alphabet, source_rng=fixed_rng)
        seq = src.generate(1000)
        assert len(seq) == 1000

    def test_zipf_not_uniform(self, alphabet, fixed_rng):
        src = ZipfIIDSource(alphabet, alpha=1.5, source_rng=fixed_rng)
        n = 20000
        seq = src.generate(n)
        counts = {word: 0 for word in alphabet}
        for s in seq:
            counts[s] += 1
        values = list(counts.values())

        assert max(values) > 2 * min(values)


class TestMarkovSource:

    def test_length(self, alphabet, fixed_rng):
        L = len(alphabet)
        P = np.ones((L, L)) / L  # transición uniforme
        src = MarkovSource(alphabet, P, source_rng=fixed_rng)
        seq = src.generate(1000)

        assert len(seq) == 1000

    def test_has_memory(self, alphabet, fixed_rng):
        L = len(alphabet)
        # matrix with a high correlation level
        P = np.eye(L) * 0.9 + (1 - 0.9) / L
        src = MarkovSource(alphabet, P, source_rng=fixed_rng)
        seq = src.generate(5000)
        same = 0
        for i in range(len(seq) - 1):
            if seq[i] == seq[i+1]:
                same += 1

        ratio = same / len(seq)

        assert ratio > 0.5


class TestBurstySource:

    def test_length(self, alphabet, fixed_rng):
        src = BurstySource(alphabet, n_bursty=2, source_rng=fixed_rng)
        seq = src.generate(1000)

        assert len(seq) == 1000

    def test_has_bursts(self, alphabet, fixed_rng):
        src = BurstySource(alphabet, n_bursty=1, p_enter=0.2, p_exit=0.1, source_rng=fixed_rng)
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
