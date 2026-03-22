import pytest

from src.link_layer.checksum import ParityChecksum, SumChecksum, CRCChecksum


@pytest.fixture
def parity_checksum():
    return ParityChecksum()

@pytest.fixture
def sum_checksum():
    return SumChecksum()

@pytest.fixture
def crc_checksum():
    return CRCChecksum("1101")

class TestParityChecksum:

    def test_parity_checksum(self, parity_checksum):
        assert parity_checksum.compute("1110") != parity_checksum.compute("1100")

    def test_checksum_limit(self, parity_checksum):
        # Same checksum, error not computed
        assert parity_checksum.compute("1010") == parity_checksum.compute("0101")


class TestSumChecksum:

    def test_sum_checksum_basic(self, sum_checksum):
        assert sum_checksum.compute("1110") == 3
        assert sum_checksum.compute("0000") == 0

    def test_sum_checksum_detects_bit_flip(self, sum_checksum):
        original = "1110"
        corrupted = "1100"
        assert sum_checksum.compute(original) != sum_checksum.compute(corrupted)

    def test_sum_checksum_limit_permutation(self, sum_checksum):
        assert sum_checksum.compute("1010") == sum_checksum.compute("0101")


class TestCRCChecksum:

    def test_crc_detects_error(self, crc_checksum):
        crc = CRCChecksum("1101")
        original = "1011001"
        corrupted = "1010001"
        assert crc.compute(original) != crc.compute(corrupted)

    def test_crc_stronger_than_parity(self, crc_checksum, parity_checksum):
        a = "1010"
        b = "0101"
        assert parity_checksum.compute(a) == parity_checksum.compute(b)
        assert crc_checksum.compute(a) != crc_checksum.compute(b)
