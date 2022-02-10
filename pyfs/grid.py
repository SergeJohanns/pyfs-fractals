from fractals import Vec
from window import Window


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
