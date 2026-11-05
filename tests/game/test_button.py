import pytest

from asdf_hero.game import Button


@pytest.fixture
def button():
    return Button(x=10, y=20, width=200, height=40)


def test_init(button):
    assert (button.x, button.y, button.width, button.height) == (10, 20, 200, 40)
    assert button.clicked is False


@pytest.mark.parametrize(
    "x, y", [(10, 20), (210, 60), (110, 40), (10, 60), (210, 20)]
)
def test_contains(button, x, y):
    assert button.contains(x, y) is True


@pytest.mark.parametrize("x, y", [(9, 40), (211, 40), (110, 19), (110, 61), (0, 0)])
def test_does_not_contain(button, x, y):
    assert button.contains(x, y) is False
