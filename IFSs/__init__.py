from typing import Callable

import numpy as np

Vec = tuple[float, float]
Map = Callable[[Vec], Vec]
IteratedFunctionSystem = list[Map]


class Window:
    def __init__(self, min_x: float, max_x: float, min_y: float, max_y: float):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def __repr__(self):
        return f"Window({self.min_x}, {self.max_x}, {self.min_y}, {self.max_y})"

    def __contains__(self, point: Vec) -> bool:
        return (
            self.min_x <= point[0] <= self.max_x
            and self.min_y <= point[1] <= self.max_y
        )

    @classmethod
    def empty(cls):
        """Return an empty window that behaves well when adding new points."""
        return cls(np.infty, -np.infty, np.infty, -np.infty)

    def include(self, point: Vec):
        """Expand the window to include the given point, if necessary."""
        x, y = point
        self.min_x = min(self.min_x, x)
        self.max_x = max(self.max_x, x)
        self.min_y = min(self.min_y, y)
        self.max_y = max(self.max_y, y)

    def pad(self, x_factor, y_factor):
        """Expand the window by a relative factor in each direction."""
        width = self.width
        height = self.height
        self.min_x -= width * x_factor / 2
        self.max_x += width * x_factor / 2
        self.min_y -= height * y_factor / 2
        self.max_y += height * y_factor / 2

    def match_aspect_ratio(self, resolution: tuple[int, int]):
        """Pad the window in one direction to match the given resolution."""
        x, y = resolution
        d_x = self.width / x
        d_y = self.height / y
        d_width = (self.height * x / y - self.width) / 2 if d_x <= d_y else 0
        d_height = (self.width * y / x - self.height) / 2 if d_x > d_y else 0
        self.min_x -= d_width
        self.max_x += d_width
        self.min_y -= d_height
        self.max_y += d_height

    @property
    def width(self):
        return self.max_x - self.min_x

    @property
    def height(self):
        return self.max_y - self.min_y


class Grid:
    def __init__(self, window: Window, resolution: tuple[int, int]):
        self.window = window
        self.resolution = resolution

    def get_coordinates(self, point: Vec):
        """Get the coordinates of the pixel corresponding to a given point.

        :param grid: The grid of pixels to get coordinates in.
        :param point: The point in the plane whose pixel to get.
        :returns: The coordinates of the pixel in the grid that contains the point.
        """
        i = (point[0] - self.window.min_x) // self.x_step
        j = (point[1] - self.window.min_y) // self.y_step
        return (int(i), self.resolution[1] - int(j))

    @property
    def x_step(self):
        return self.window.width / self.resolution[0]

    @property
    def y_step(self):
        return self.window.height / self.resolution[1]
