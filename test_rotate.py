"""Test file for rotate."""

import pytest
import random
from math import sqrt
from rotate_main import Vertex, near


@pytest.fixture()
def two_verteces():
    """Create two points on sphere."""
    vert_1 = Vertex(-0.65, -1.55, 2.49)
    vert_2 = Vertex(2.76, -0.18, 1.16)

    return vert_1, vert_2


@pytest.fixture()
def random_vertex():
    """Create random vertex on unit-sphere."""
    x = random.random(-1, 1)

    tmp_y = sqrt(1 - x**2)
    y = random.random(-tmp_y, tmp_y)

    z = random.choice([-1, 1]) * sqrt(1 - x**2 - y**2)

    return Vertex(x, y, z)


@pytest.fixture()
def two_random_verteces():
    """Create two random points on unit-sphere."""
    vert_1 = random_vertex()
    vert_2 = random_vertex()

    return vert_1, vert_2


def test_near(two_verteces):
    """Test near function."""
    v_1, v_2 = two_verteces
    assert near(v_1, Vertex(-0.65001, -1.55004, 2.49003))
    assert near(v_2, Vertex(2.760001, -0.180002, 1.16002))


def test_magic(two_verteces):
    """Test magic methods with Vertex."""
    v_1, v_2 = two_verteces

    # __str__
    assert str(v_1) == "(x: -0.65, y: -1.55, z: 2.49)"
    assert str(v_2) == "(x: 2.76, y: -0.18, z: 1.16)"

    # __iter__
    assert list(iter(v_1)) == [-0.65, -1.55, 2.49]
    assert list(iter(v_2)) == [2.76, -0.18, 1.16]

    # __eq__
    assert v_1 == Vertex(-0.65, -1.55, 2.49)
    assert v_1 == Vertex(-0.65001, -1.55004, 2.49003)
    assert v_2 == Vertex(2.76, -0.18, 1.16)
    assert v_2 == Vertex(2.760001, -0.180002, 1.16002)

    # __add__
    assert v_1 + v_2 == Vertex(2.11, -1.73, 3.65)

    # __neg__
    assert -v_1 == Vertex(0.65, 1.55, -2.49)
    assert -v_2 == Vertex(-2.76, 0.18, -1.16)

    # __sub__
    assert v_1 - v_2 == Vertex(-3.41, -1.37, 1.33)

    # __abs__
    assert near(abs(v_1), 3)
    assert near(abs(v_2), 3)

    # __rmul__
    assert 5 * v_1 == Vertex(-3.25, -7.75, 12.45)
    assert 7 * v_2 == Vertex(19.32, -1.26, 8.12)

    # __getitem__
    assert v_1["x"] == -0.65
    assert v_1[0] == -0.65

    # __mul__
    assert v_1 * 5 == Vertex(-3.25, -7.75, 12.45)
    assert v_2 * 7 == Vertex(19.32, -1.26, 8.12)

    # __truediv__
    assert Vertex(-3.25, -7.75, 12.45) / 5 == v_1
    assert Vertex(19.32, -1.26, 8.12) / 7 == v_2
