from random import choice, uniform
from typing import Callable

import numpy as np
from PIL import Image

# Colors picked from the Nord theme [https://www.nordtheme.com/]
COLORS_HEX = {0: "2e3440", 1: "ebcb8b"}
RESOLUTION = (720, 1440)
PADDING = 0

ITERATIONS = 50
POINTS = 500000

Vec = tuple[float, float]
Map = Callable[[Vec], Vec]
IteratedFunctionSystem = list[Map]
Color = tuple[int, int, int]
Grid = tuple[np.ndarray, np.ndarray]
Window = tuple[tuple[float, float], tuple[float, float]]


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


def make_golden_dragon() -> IteratedFunctionSystem:
    # https://larryriddle.agnesscott.org/ifs/heighway/goldenDragon.htm
    phi = (1 + np.sqrt(5)) / 2
    r = (1 / phi) ** (1 / phi)

    def make_function(rotation: float, scaling: float, translation: Vec) -> Map:
        cos = scaling * np.cos(rotation)
        sin = scaling * np.sin(rotation)
        dx, dy = translation

        def map(point):
            x, y = point
            return (cos * x - sin * y + dx, sin * x + cos * y + dy)

        return map

    f1 = make_function(np.arccos((1 + r**2 - r**4) / (2 * r)), r, (0, 0))
    f2 = make_function(
        np.deg2rad(180) - np.arccos((1 + r**4 - r**2) / (2 * r**2)),
        r**2,
        (1, 0),
    )
    return [f1, f2]


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
    # colors = {0: (46, 52, 64), 1: (76, 86, 106)}
    size = 1.5 + 2 * PADDING
    x, y = (-0.35 - PADDING, -0.55 - PADDING)

    high_res = (3 * RESOLUTION[0], 3 * RESOLUTION[1])
    colors = {k: hex2color(v) for k, v in COLORS_HEX.items()}
    min_window = ((x, x + size), (y, y + size))
    (a, b), (c, d) = size_window(min_window, high_res)
    xs = np.linspace(a, b, high_res[0])
    ys = np.linspace(c, d, high_res[1])
    ifs = make_golden_dragon()
    raster = make_raster(colors, (xs, ys), get_point, ifs)
    im = Image.fromarray(raster).resize(RESOLUTION)
    im.save("output.png")
