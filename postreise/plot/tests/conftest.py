import pytest
from matplotlib import pyplot as plt


@pytest.fixture(autouse=True)
def plt_close():
    yield
    plt.close("all")
