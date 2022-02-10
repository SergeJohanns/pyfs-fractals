from . import IteratedFunctionSystem, Vec


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


def get() -> IteratedFunctionSystem:
    return make_levy_c_curve()
