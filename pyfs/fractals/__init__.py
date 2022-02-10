from typing import Callable

Vec = tuple[float, float]
Map = Callable[[Vec], Vec]
IteratedFunctionSystem = list[Map]
