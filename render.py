from importlib import import_module
from random import choice, uniform
from typing import Callable

import numpy as np
from alive_progress import alive_bar
from PIL import Image

from IFSs import Grid, IteratedFunctionSystem, Vec, Window

# Configuration
IFS_NAME = "golden_dragon"
## Colors picked from the Nord theme [https://www.nordtheme.com/]
COLORS_HEX = {0: "2e3440", 1: "ebcb8b"}
RESOLUTION = (1920, 1080)
PADDING = 2
ZOOM = 3
ITERATIONS = 50
POINTS = 500000

# Internals
IFS_PATH = "IFSs.{}"

Color = tuple[int, int, int]


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
    resolution: tuple[int, int],
    get_point: Callable[[], Vec],
    ifs: IteratedFunctionSystem,
    padding: float,
    quiet=False,
) -> np.ndarray:
    """Create a raster image of the fractal.

    :param colors: Dict mapping the assigned int to an appropriate color.
    :param resolution: The resolution at which to render the image.
    :param get_point: The distribution function for getting random points.
    :param ifs: The Iterated Function System that generates the fractal.
    :param padding: Relative padding to add to each side.
    :param quiet: If True, do not perform any logging of progress.
    :returns: A raster image of the fractal within the given grid.
    """
    window = Window.empty()

    points = set()

    def compute_points():
        for _ in range(POINTS):
            x, y = get_point()
            proj = project(ifs, (x, y))
            points.add(proj)
            window.include(proj)
            yield

    x_res, y_res = resolution
    out = np.ndarray((y_res, x_res, 3), dtype=np.uint8)

    def zero_init(resolution: tuple[int, int]):
        x_res, y_res = resolution
        for j in range(y_res):
            for i in range(x_res):
                out[j, i] = colors[0]
                yield

    def draw_points(grid: Grid):
        (xs, ys) = grid
        for point in points:
            i, j = get_coordinates(grid, point)
            if 0 <= i < len(xs) and 0 <= j < len(ys):
                out[j, i] = colors[1]
            yield

    if quiet:
        for _ in compute_points():
            pass
        window.pad(padding, padding)
        window.match_aspect_ratio(resolution)
        for _ in zero_init(resolution):
            pass
        for _ in draw_points(window.get_grid(resolution)):
            pass
    else:
        with alive_bar(POINTS, title="   Computing points:") as bar:
            for _ in compute_points():
                bar()
        window.pad(padding, padding)
        window.match_aspect_ratio(resolution)
        cells = resolution[0] * resolution[1]
        with alive_bar(cells, title="Initializing raster:") as bar:
            for _ in zero_init(resolution):
                bar()
        with alive_bar(POINTS, title="     Drawing points:") as bar:
            for _ in draw_points(window.get_grid(resolution)):
                bar()
    return out


def get_point() -> Vec:
    return (uniform(-10, 10), uniform(-10, 10))


def hex2color(hex: str) -> Color:
    return (int(hex[:2], 16), int(hex[2:4], 16), int(hex[4:], 16))


if __name__ == "__main__":
    ifs_module = import_module(IFS_PATH.format(IFS_NAME))
    ifs = ifs_module.get()
    high_res = (ZOOM * RESOLUTION[0], ZOOM * RESOLUTION[1])
    colors = {k: hex2color(v) for k, v in COLORS_HEX.items()}
    raster = make_raster(colors, high_res, get_point, ifs, PADDING)
    im = Image.fromarray(raster).resize(RESOLUTION)
    im.save("output.png")
