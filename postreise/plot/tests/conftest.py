import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def plt_close():
    yield
    plt.close("all")
