"""Rotation of 3D figure, calculation part.

06.2020
"""

from math import sin, cos, sqrt
from numpy import array as np_arr
from numpy import ones
from itertools import combinations, product
from functools import reduce

EPS = 0.005
VARS = {"x": 0, "y": 1, "z": 2}


class Figure():
    """Abstract class of figures."""

    def __iter__(self):
        """Iterator on the verteces."""
        for vertex in self.verteces:
            yield vertex

    def __add__(self, angle):
        """Add-operator for turning by the angle.

        Change tetrahedron.
        """
        return self.rotate(angle)

    def rotate(self, angle):
        """Rotate vertex by the angle.

        Change coordinates.
        """
        for vertex in self:
            vertex.rotate(angle)

        for face in self.faces:
            face.rotate(angle)

        return self

    def __str__(self):
        """String format for Tetrahedron."""
        return "\n".join([str(v) for v in self])


class Tetrahedron(Figure):
    """Simple regular Tetrahedron with center in O."""

    def __init__(self, rho):
        """Data of Tetrahedron.

        In cartesian coordinates, huh
        """
        self.verteces = [
            rho * Vertex(1, 0, -1 / sqrt(2), 0),
            rho * Vertex(-1, 0, -1 / sqrt(2), 1),
            rho * Vertex(0, 1, 1 / sqrt(2), 2),
            rho * Vertex(0, -1, 1 / sqrt(2), 3)
        ]
        self.faces = [
            Face(vert_s) for vert_s in combinations(self.verteces, 3)
        ]

        self.faces[-1].always_unvisiable = True


class Cube(Figure):
    """Simple regular Cube."""

    def __init__(self, rho):
        """Data of Cube.

        In cartesian coordinates.
        """
        self.verteces = list(map(lambda x: rho * Vertex(*(x[1]), nu=x[0]),
                                 enumerate(product([1, -1], repeat=3))))

        self.faces = []
        faces = [(0, 1, 3, 2), (5, 1, 3, 7), (4, 6, 7, 5), (4, 0, 2, 6),
                 (6, 2, 3, 7), (4, 0, 1, 5)]
        for face_vert in faces:
            self.faces.append(Face([self.verteces[i] for i in face_vert]))

        self.faces[-1].always_unvisiable = True


class Face:
    """Face of the tetrahedron."""

    def __init__(self, verteces, color=("#50c878", "#303030")):
        """Initialization for face of the tetrahedron."""
        self.verteces = verteces
        self.vector = Vertex(reduce(lambda x, y: x + y, verteces))
        self.visiable = True
        self.always_unvisiable = False
        self.default_color = color

    def rotate(self, angle):
        """Rotate face - its vector."""
        self.vector.coords = angle.rot_matrix.dot(self.vector.coords)
        self.visiable = self.if_visiable()

    def if_visiable(self):
        """Check if face is visiable."""
        return self.vector["y"] < 0

    def __iter__(self):
        """Define iterator on verteces."""
        for vert in self.verteces:
            yield vert

    def __nonzero__(self):
        """Boolean value."""
        return self.visiable

    def get_color(self):
        """Return dinamic color of the face."""
        cur_color = 0 if self.vector["y"] < 0 else 1  # inner or outer color
        vect = self.vector[2]
        vect *= 1 if not cur_color else -0.5

        cur_color = self.default_color[cur_color]

        return add_shadow(cur_color, vect)


class Vertex:
    """Vertex in R^3."""

    def __init__(self, x=0, y=0, z=0, nu=0):
        """Initialization of Vertex.

        In cartesian coordinates (x, y, z)
        """
        if isinstance(x, Vertex):
            x, y, z = x
        self.coords = np_arr([x, y, z])
        self.nu = nu

    def rotate(self, angle):
        """Rotate vertex by the angle.

        Change coordinates.
        """
        self.coords = angle.rot_matrix.dot(self.coords)

    def __str__(self):
        """String format for Vertex."""
        return "(x: {}, y: {}, z: {})".format(*self.coords)

    def __iter__(self):
        """Iterator on coordinates."""
        for coord in self.coords:
            yield coord

    def __add__(self, other):
        """Allow to add points (as vectors)."""
        return Vertex(*(self.coords + other.coords), nu=self.nu)

    def __neg__(self):
        """Define behavior for negation."""
        return Vertex(*(-self.coords), nu=self.nu)

    def __sub__(self, other):
        """Allow to subtract points (as vectors)."""
        return Vertex(*(self.coords + (-other.coords)), nu=self.nu)

    def __abs__(self):
        """Calculate absolute value(lenght) of the vector."""
        return sqrt(sum(map(lambda x: x**2, self.coords)))

    def __rmul__(self, alpha):
        """Define homothety for point (vector)."""
        return Vertex(*(alpha * self.coords), nu=self.nu)

    def __eq__(self, other):
        """Define equality of points."""
        return near(self, other)

    def __getitem__(self, key):
        """Define getter for coords."""
        if isinstance(key, str):
            key = VARS[key]
        return self.coords[key]

    def __mul__(self, alpha):
        """Define homothety of the point (vector)."""
        return Vertex(*(self.coords * alpha), nu=self.nu)

    def __truediv__(self, alpha):
        """Define division of the point (vector)."""
        return Vertex(*(self.coords / alpha), nu=self.nu)

    def projection(self):
        """Return projection on zOx plane."""
        return self["x"], self["z"]


class Angle:
    """Angle object with appropriate operations."""

    def __init__(self, alpha, beta, gamma):
        """Initialization of the angle."""
        self.alpha, self.beta, self.gamma = alpha, beta, gamma

        # Euler angles
        self.rot_matrix = np_arr(
            [[
                cos(alpha) * cos(gamma) - cos(beta) * sin(alpha) * sin(gamma),
                -cos(gamma) * sin(alpha) - cos(alpha) * cos(beta) * sin(gamma),
                sin(beta) * sin(gamma)
            ], [
                cos(beta) * cos(gamma) * sin(alpha) + cos(alpha) * sin(gamma),
                cos(alpha) * cos(beta) * cos(gamma) - sin(alpha) * sin(gamma),
                -cos(gamma) * sin(beta)
            ], [sin(alpha) * sin(beta),
                cos(alpha) * sin(beta),
                cos(beta)]])

    def __add__(self, other):
        """Standard addition of vectors."""
        return Angle(self.alpha + other.alpha,
                     self.beta + other.beta,
                     self.gamma + other.gamma)

    def __neg__(self):
        """Standard negotiation of the vector."""
        return Angle(-self.alpha, -self.beta, -self.gamma)

    def __sub__(self, other):
        """Standard subtraction of the vector."""
        return self + (-other)

    def __truediv__(self, nu):
        """Standard division by number on vectors."""
        return Angle(self.alpha / nu, self.beta / nu, self.gamma / nu)


def near(obj_1, obj_2):
    """Check if obj_1 and obj_2 are near.

    That means that points are equal.
    """
    return abs(obj_1 - obj_2) < EPS


def add_shadow(color, z_pos):
    """Add shadow to the color depending on z-coord."""
    vect = ones(3) * z_pos

    color = (color[1:3], color[3:5], color[5:])
    color = np_arr(list(map(lambda x: int(x, base=16), color)))

    color += (vect // 4).astype(int)

    color = map(lambda x: x if x >= 0 else 0, color)
    color = map(lambda x: x if x <= 255 else 255, color)

    color = map(lambda x: hex(x)[2:].zfill(2), color)

    return "#" + "".join(color)
