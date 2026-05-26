import pytest


class CleanChannel():

    def apply_noise(self, bits):
        return bits


@pytest.fixture
def dummy_channel():
    return CleanChannel()

