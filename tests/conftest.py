import pytest
from .utils import get_macro
from mikroj.language.transpile import TranspileRegistry


@pytest.fixture(scope="session")
def analyze_particles():
    """Analyze particles."""
    return get_macro("analyze_particles.ijm")


@pytest.fixture(scope="session")
def parameters():
    """Analyze particles."""
    return get_macro("parameters.ijm")


@pytest.fixture(scope="session")
def transpile_registry():
    return TranspileRegistry()
