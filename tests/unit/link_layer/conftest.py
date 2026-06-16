import pytest

from link_layer.link_layer import LinkLayer


@pytest.fixture
def example_link_layer():
    return LinkLayer()