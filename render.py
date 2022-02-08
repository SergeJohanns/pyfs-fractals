from importlib import import_module
from random import choice, uniform
from typing import Callable

import numpy as np
from PIL import Image

from IFSs import IteratedFunctionSystem, Vec, Window

# Configuration
IFS_NAME = "golden_dragon"
## Colors picked from the Nord theme [https://www.nordtheme.com/]
COLORS_HEX = {0: "2e3440", 1: "ebcb8b"}
RESOLUTION = (720, 1440)
PADDING = 0
ITERATIONS = 50
POINTS = 500000

# Internals
IFS_PATH = "IFSs.{}"
ZOOM = 3

Color = tuple[int, int, int]
Grid = tuple[np.ndarray, np.ndarray]


def get_coordinates(grid: Grid, point: Vec) -> tuple[int, int]:
    """Get the coordinates of the pixel corresponding to a given point.

    :param grid: The grid of pixels to get coordinates in.
    :param point: The point in the plane whose pixel to get.
    :returns: The coordinates of the pixel in the grid that contains the point.
    """
    xs, ys = grid
    x_step = (xs[-1] - xs[0]) / len(xs)
    y_step = (ys[-1] - ys[0]) / len(ys)
    x, y = point
    i, j = ((x - xs[0]) // x_step, (y - ys[0]) // y_step)
    return (int(i), len(ys) - int(j))


def project(ifs: IteratedFunctionSystem, point: Vec) -> Vec:
    """Project a point by repeatedly applying functions from the IFS.

    :param ifs: The Iterated Function System to use for projection.
    :param point: The point in the plane to repeatedly project.
    :returns: A point obtained by applying random functions from the IFS.
    """
    curr = point
    for _ in range(ITERATIONS):
        curr = choice(ifs)(curr)
    return curr


def make_raster(
    colors: dict[int, Color],
    grid: Grid,
    get_point: Callable[[], Vec],
    ifs: IteratedFunctionSystem,
) -> np.ndarray:
    """Create a raster image of the fractal.

    :param colors: Dict mapping the assigned int to an appropriate color.
    :param grid: The axes of the grid the fractal should be rendered in.
    :param get_point: The distribution function for getting random points.
    :param ifs: The Iterated Function System that generates the fractal.
    :returns: A raster image of the fractal within the given grid.
    """
    xs, ys = grid
    out = np.ndarray((len(ys), len(xs), 3), dtype=np.uint8)
    for j in range(len(ys)):
        for i in range(len(xs)):
            out[j, i] = colors[0]
    k = 0
    for _ in range(POINTS):
        x, y = get_point()
        k += 1
        proj = project(ifs, (x, y))
        i, j = get_coordinates(grid, proj)
        if 0 <= i < len(xs) and 0 <= j < len(ys):
            out[j, i] = colors[1]
    print(k)
    return out


def size_window(min_window: Window, dim: tuple[int, int]) -> Window:
    """Pad the minimum window to have the same proportions as the target
    resolution.

    :param min_window: Smallest allowable window resolution to ensure the entire
        fractal is included and approximately centered.
    :param dim: Resolution of the target window.
    :returns: A window of the plane of the same proportions as the resolution.
    """
    (a, b), (c, d) = min_window
    x, y = dim
    d_width = (x / y - 1) * (b - a) / 2 if x >= y else 0
    d_height = (y / x - 1) * (d - c) / 2 if x < y else 0
    return (a - d_width, b + d_width), (c - d_height, d + d_height)


def get_point() -> Vec:
    return (uniform(-10, 10), uniform(-10, 10))


def hex2color(hex: str) -> Color:
    return (int(hex[:2], 16), int(hex[2:4], 16), int(hex[4:], 16))


if __name__ == "__main__":
    ifs_module = import_module(IFS_PATH.format(IFS_NAME))
    ifs, min_window = ifs_module.get()
    high_res = (ZOOM * RESOLUTION[0], ZOOM * RESOLUTION[1])
    colors = {k: hex2color(v) for k, v in COLORS_HEX.items()}
    (a, b), (c, d) = size_window(min_window, high_res)
    xs = np.linspace(a, b, high_res[0])
    ys = np.linspace(c, d, high_res[1])
    raster = make_raster(colors, (xs, ys), get_point, ifs)
    im = Image.fromarray(raster).resize(RESOLUTION)
    im.save("output.png")
