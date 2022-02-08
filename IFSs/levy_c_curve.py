from . import IFSModule, IteratedFunctionSystem, Vec


def make_levy_c_curve() -> IteratedFunctionSystem:
    # https://en.wikipedia.org/wiki/L%C3%A9vy_C_curve
    def f1(point: Vec) -> Vec:
        z = complex(*point)
        out = (1 - 1j) * z / 2
        return out.real, out.imag

    def f2(point: Vec) -> Vec:
        z = complex(*point)
        out = 1 + (1 + 1j) * (z - 1) / 2
        return out.real, out.imag

    return [f1, f2]


height = 1.3
y = -0.375
width = 2.05
x = 0.5
min_window = ((x - width / 2, x + width / 2), (y - height / 2, y + height / 2))


def get() -> IFSModule:
    return make_levy_c_curve(), min_window
