from typing import Callable

Vec = tuple[float, float]
Map = Callable[[Vec], Vec]
IteratedFunctionSystem = list[Map]
Window = tuple[tuple[float, float], tuple[float, float]]
IFSModule = tuple[IteratedFunctionSystem, Window]
