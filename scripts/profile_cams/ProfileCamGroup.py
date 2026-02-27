from dataclasses import dataclass

# typing imports
from numpy.typing import NDArray
from typing import Dict, List
from ROI import ROI
from PhysicalAxis import PhysicalAxis

@dataclass
class ProfileCamGroup:
    shot_numbers: List[int]
    processed_images: List[NDArray[float]]
    lineouts: NDArray[float]
    lineout_mean: NDArray[float]
    lineout_stderr: NDArray[float]
    x: PhysicalAxis                # assumes x is the same for every image (requires the same roi and calib for all images)
    y: PhysicalAxis

    _calib_id: str
    _roi: ROI