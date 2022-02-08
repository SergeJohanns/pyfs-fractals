import numpy as np

from . import IFSModule, IteratedFunctionSystem, Map, Vec


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


size = 1.5
x, y = (-0.35, -0.55)
min_window = ((x, x + size), (y, y + size))


def get() -> IFSModule:
    return make_golden_dragon(), min_window
