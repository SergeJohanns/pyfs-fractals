from typing import Callable

import numpy as np

Vec = tuple[float, float]
Map = Callable[[Vec], Vec]
IteratedFunctionSystem = list[Map]
Grid = tuple[np.ndarray, np.ndarray]


class Window:
    def __init__(self, min_x: float, max_x: float, min_y: float, max_y: float):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def __repr__(self):
        return f"Window({self.min_x}, {self.max_x}, {self.min_y}, {self.max_y})"

    @classmethod
    def empty(cls):
        """Return an empty window that behaves well when adding new points."""
        return cls(np.infty, -np.infty, np.infty, -np.infty)

    def include(self, point: Vec):
        x, y = point
        if x < self.min_x:
            self.min_x = x
        elif x > self.max_x:
            self.max_x = x
        if y < self.min_y:
            self.min_y = y
        elif y > self.max_y:
            self.max_y = y

    def pad(self, x_factor, y_factor):
        width = self.width
        height = self.height
        self.min_x -= width * x_factor / 2
        self.max_x += width * x_factor / 2
        self.min_y -= height * y_factor / 2
        self.max_y += height * y_factor / 2

    def match_aspect_ratio(self, resolution: tuple[int, int]):
        x, y = resolution
        d_x = self.width / x
        d_y = self.height / y
        d_width = (self.height * x / y - self.width) / 2 if d_x <= d_y else 0
        d_height = (self.width * y / x - self.height) / 2 if d_x > d_y else 0
        self.min_x -= d_width
        self.max_x += d_width
        self.min_y -= d_height
        self.max_y += d_height

    def get_grid(self, resolution: tuple[int, int]) -> Grid:
        xs = np.linspace(self.min_x, self.max_x, resolution[0])
        ys = np.linspace(self.min_y, self.max_y, resolution[1])
        return (xs, ys)

    @property
    def width(self):
        return self.max_x - self.min_x

    @property
    def height(self):
        return self.max_y - self.min_y
