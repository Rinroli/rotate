#!/usr/bin/env python3
"""Rotation of 3D figure, drawing part.

06.2020
"""

from tkinter import Frame, Canvas, Pack
from rotate_main import Tetrahedron, Angle, Vertex, Cube, add_shadow
from random import uniform
from math import sqrt
from time import time

COMPONENTS = ["vertex", "edge", "inner", "face", "center"]
COLORS = ["purple", "blue", "green", "pink", "yellow"]
FPS = 60
PRINT_FPS = False


class Wind(Frame):
    """Main window."""

    def __init__(self, figure):
        """Initialization of main window."""
        Frame.__init__(self)
        Pack.config(self)

        self.canvas = Canvas(self, width="900", height="850", bd=0)  # 500, 450

        self.figure = figure
        self.r_angle = Angle(0.015, 0.015, 0.015)
        self.step = 0

        new_angle = Angle(*[uniform(-0.03, 0.03) for i in range(3)])
        self.dif = (new_angle - self.r_angle) / (5 * FPS)

        self.config = {
            "vertex": [False, self._draw_verteces],
            "edge": [False, self._draw_edges],
            "inner": [True, self._draw_clever_edges],
            "center": [True, self._draw_solid_vertex],
            "face": [True, self._draw_faces]
        }

        self.canvas.focus_set()

        self.canvas.bind("<e>", lambda event: self.change_bool("edge"))
        self.canvas.bind("<v>", lambda event: self.change_bool("vertex"))
        self.canvas.bind("<i>", lambda event: self.change_bool("inner"))
        self.canvas.bind("<c>", lambda event: self.change_bool("center"))
        self.canvas.bind("<f>", lambda event: self.change_bool("face"))

        self.canvas.pack()

    def change_bool(self, obj):
        """Change bool value True <-> False."""
        self.config[obj][0] = (self.config[obj][0] + 1) % 2

    def _draw_object(self, obj, *args, **kwargs):
        if self.config[obj][0]:
            self.config[obj][1](*args, **kwargs)
            return True
        return False

    def draw_tetra(self):
        """Draw tetrahedron on the canvas."""
        if not self._draw_object("face"):
            self._draw_object("vertex")
            self._draw_object("edge")
            self._draw_object("center", Vertex(), r=10)
            self._draw_object("inner")

    def redraw_tetra(self, ti=0):
        """Redraw tetrahedron on the canvas with recursion."""
        if PRINT_FPS:
            print(1 / (time() - ti))
            ti = time()
        self.after(int((1 / FPS) * 1000), self.redraw_tetra, ti)
        for tag in COMPONENTS:
            self.canvas.delete(tag)
        self.draw_tetra()
        self.update()

        if self.step == 5 * FPS:
            self.step = 0
            new_angle = Angle(*[uniform(-0.02, 0.02) for i in range(3)])
            self.dif = (new_angle - self.r_angle) / (5 * FPS)

        self.figure.rotate(self.r_angle)
        self.r_angle += self.dif

        self.step += 1

    def _draw_faces(self):
        """Draw all faces."""
        for face in self.figure.faces:
            if not face.always_unvisiable and not face.visiable:
                self._polygon_on_canvas(face,
                                        fill=face.get_color(),
                                        tag="face")

        self._draw_object("edge")
        self._draw_object("center", Vertex(), r=10)
        self._draw_object("inner")

        for face in self.figure.faces:
            if not face.always_unvisiable and face.visiable:
                self._polygon_on_canvas(face,
                                        fill=face.get_color(),
                                        tag="face")
        self._draw_object("vertex")

    def _polygon_on_canvas(self, vert_s, **kwargs):
        """Draw polygon on canvas."""
        self.canvas.create_polygon(_make_polygon(vert_s), **kwargs)

    def _line_on_canvas(self, vert_1, vert_2, **kwargs):
        """Draw line with tag on canvas."""
        self.canvas.create_line(_make_line(vert_1, vert_2), **kwargs)

    def _oval_on_canvas(self, vertex, r=3, fill="red", **kwargs):
        """Draw oval with tag & color on canvas."""
        self.canvas.create_oval(*_make_small_circle(*vertex.projection(), r=r),
                                fill=fill,
                                **kwargs)

    def _draw_solid_vertex(self, vertex, tag="center", r=10, **kwargs):
        """Draw solid 3-color vertex with shadows."""
        centers = [round(r / 5), int(r / 2.5)]
        colors = ["#c70000", "#e60000"]

        self._oval_on_canvas(vertex,
                             r=r,
                             fill=add_shadow("#b00000", vertex["z"]),
                             tag=tag,
                             **kwargs)
        for center, color in zip(centers, colors):
            self._oval_on_canvas(vertex + Vertex(0, 0, center),
                                 r=r - center,
                                 fill=add_shadow(color, vertex["z"]),
                                 width=0,
                                 tag=tag,
                                 **kwargs)

    def _draw_edges(self):
        """Draw all edges of tetrahedron."""
        for vert in self.figure.verteces:
            self._draw_clever_edges(in_v=vert, full=True, tag="edge", r=5)

    def _draw_clever_edges(self, full=False, in_v=Vertex(), tag="inner", r=10):
        """Draw edges of tetrahedron from given vertex.

        'Clever' means that edge will not intersept vertex.
        """
        lenght = 2 if full else 4
        incedent = "center" if tag == "inner" else "vertex"
        for vert in self.figure:
            if vert != in_v:
                vert = vert - in_v
                if self.config[incedent][0]:
                    inner_end = (vert / abs(vert))
                    if vert["y"] > 0:
                        inner_end /= sqrt(inner_end["x"]**2 +
                                          inner_end["z"]**2)
                    inner_end *= r

                    if abs(inner_end) < abs(vert):
                        self._line_on_canvas(in_v + vert / lenght,
                                             in_v + inner_end,
                                             tag=tag)
                else:
                    self._line_on_canvas(in_v + vert / lenght,
                                         in_v,
                                         tag=tag)

    def _draw_verteces(self):
        """Draw verteces of tetrahedron."""
        if self.config["face"][0]:
            vert_visiable = [[False, vert] for vert in self.figure.verteces]
            for face in self.figure.faces:
                if face.visiable:
                    for vertex in face:
                        vert_visiable[vertex.nu][0] = True
        else:
            vert_visiable = [[True, vert] for vert in self.figure.verteces]

        for vertex in vert_visiable:
            if vertex[0]:
                self._draw_solid_vertex(vertex[1], tag="vertex", r=5)


def _convert_coords(point):
    """Convert coords to the new at the center of canvas."""
    return [point[0] + 450, -point[1] + 425]  # 250, 225


def _make_small_circle(x, y, r=5):
    """Make small circle in point (x, y).

    Circle with radius r moved to (0, 0) center of canvas.
    """
    x, y = _convert_coords((x, y))
    return (x - r, y - r, x + r, y + r)


def _make_line(vert_1, vert_2):
    """Move line to the center of canvas."""
    return _make_polygon([vert_1, vert_2])


def _make_polygon(vert_s):
    """Make proper coords for polygon."""
    res = []
    for vert in vert_s:
        res += _convert_coords(vert.projection())
    return res


if __name__ == '__main__':
    T = Tetrahedron(200)
    # C = Cube(200)
    ex = Wind(T)

    ex.draw_tetra()
    try:
        # ex.run()
        ex.redraw_tetra()
    except RecursionError:
        print("All!")

    ex.mainloop()
