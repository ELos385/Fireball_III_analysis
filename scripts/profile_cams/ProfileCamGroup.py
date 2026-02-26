from dataclasses import dataclass

# typing imports
from numpy.typing import NDArray
from typing import Dict, List

@dataclass
class ProfileCamGroup:
    shot_numbers: List[int]
    processed_images: List[NDArray[float]]
    lineouts: NDArray[float]
    lineout_mean: NDArray[float]
    lineout_stderr: NDArray[float]