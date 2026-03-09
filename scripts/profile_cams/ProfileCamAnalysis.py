import numpy as np

import os, sys
from pathlib import Path

# typing imports
from numpy.typing import NDArray
from typing import Dict, List
from LAMP.diagnostic import Diagnostic
from enum import Enum

from ProfileCamGroup import ProfileCamGroup
from PhysicalAxis import PhysicalAxis
from ROI import ROI


class Normalisation(Enum):
    NONE = "none"
    AREA = "area"
    MAX = "max"

class ProfileCamAnalysis:
    """
    will allow you to load multiple images, grouping them by shot type (eg "gas" "plasma")
    can take lineouts in a region of interest
    then average over shots of a given type
    """

    def __init__(self, diagnostic: Diagnostic, calib_id: str):
        self.diagnostic = diagnostic
        self.calib_id = calib_id

    def _normalise(self, lineout: NDArray[float], mode: Normalisation) -> NDArray[float]:
        match mode:
            case Normalisation.NONE:
                return lineout
                
            case Normalisation.AREA:
                area = np.trapezoid(lineout)
                return lineout / area if area != 0 else lineout

            case Normalisation.MAX:
                m = np.max(lineout)
                return lineout / m if m != 0 else lineout

            
    def compare_groups(self,
                       shot_groups: Dict[str, List[int]],
                       roi: ROI,
                       normalisation: Normalisation = Normalisation.NONE
                      ) -> Dict[str, ProfileCamGroup]:
        results = {}
        
        for shot_type, shots_list in shot_groups.items():
            all_lineouts = []
            all_images = []

            x_vals = None
            y_vals = None
            reference_shape = None

            for shot in shots_list:

                shot_dict = {"shot" : [shot]}
                img, x,y = self.diagnostic.get_proc_shot(shot_dict, self.calib_id)


                if x_vals is None:
                    x_vals = x
                    y_vals = y
                    reference_shape = img.shape
                else:
                    shape_changed = img.shape != reference_shape
                    x_changed = not np.array_equal(x, x_vals)
                    y_changed = not np.array_equal(y, y_vals)
                    if shape_changed or x_changed or y_changed:
                        raise RuntimeError(f"calibration has changed within {shot_type}")

                
                all_images.append(img)

                lineout = roi.lineout(img)
                lineout = self._normalise(lineout, normalisation)
                all_lineouts.append(lineout)

            all_lineouts = np.asarray(all_lineouts)
            
            scale = self.diagnostic.calib_dict.get("scale", {})
            x_units = scale.get("x_units", "None")
            y_units = scale.get("y_units", "None")
     
            results[shot_type] = ProfileCamGroup(
                shot_numbers = shots_list,
                processed_images = all_images,
                lineouts = all_lineouts,
                lineout_mean = np.mean(all_lineouts, axis=0),
                lineout_stderr = np.std(all_lineouts, axis=0, ddof=1) / np.sqrt(len(all_lineouts)),
                x = PhysicalAxis(x_vals, x_units),
                y = PhysicalAxis(y_vals, y_units),
                _calib_id = self.diagnostic.calib_id,
                _roi = roi
            )

        return results