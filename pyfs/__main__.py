from functools import wraps
from importlib import import_module
from random import choice, uniform
from typing import Callable

import numpy as np
from alive_progress import alive_bar
from PIL import Image

from fractals import IteratedFunctionSystem, Vec
from grid import Grid
from window import Window

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
IFS_PATH = "fractals.{}"

Color = tuple[int, int, int]


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


def use_bar(title: str, items: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, quiet=False, **kwargs):
            if quiet:
                for _ in func(*args, **kwargs):
                    pass
            else:
                with alive_bar(items, title=title) as bar:
                    for _ in func(*args, **kwargs):
                        bar()

        return wrapper

    return decorator


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

    @use_bar("   Computing points:", POINTS)
    def compute_points():
        for _ in range(POINTS):
            x, y = get_point()
            proj = project(ifs, (x, y))
            points.add(proj)
            window.include(proj)
            yield

    compute_points(quiet=quiet)

    x_res, y_res = resolution
    out = np.ndarray((y_res, x_res, 3), dtype=np.uint8)
    cells = resolution[0] * resolution[1]

    @use_bar("Initializing raster:", cells)
    def zero_init(resolution: tuple[int, int]):
        x_res, y_res = resolution
        for j in range(y_res):
            for i in range(x_res):
                out[j, i] = colors[0]
                yield

    window.pad(padding, padding)
    window.match_aspect_ratio(resolution)
    zero_init(resolution, quiet=quiet)

    @use_bar("     Drawing points:", POINTS)
    def draw_points(grid: Grid):
        for point in points:
            if point in grid.window:
                i, j = grid.get_coordinates(point)
                out[j, i] = colors[1]
            yield

    draw_points(Grid(window, resolution), quiet=quiet)
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
