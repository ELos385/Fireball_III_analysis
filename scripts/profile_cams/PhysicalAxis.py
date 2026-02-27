from dataclasses import dataclass
from numpy.typing import NDArray

@dataclass
class PhysicalAxis:
    values: NDArray[float]
    units: str