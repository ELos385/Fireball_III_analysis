import numpy as np

import os, sys
from pathlib import Path

# typing imports
from numpy.typing import NDArray
from typing import Dict, List
from LAMP.diagnostic import Diagnostic
from enum import Enum

from ProfileCamGroup import ProfileCamGroup
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
    and plot a comparison between these types
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

            for shot in shots_list:

                shot_dict = {"shot" : [shot]}
                img, x,y = self.diagnostic.get_proc_shot(shot_dict, self.calib_id)
                all_images.append(img)

                lineout = roi.lineout(img)
                lineout = self._normalise(lineout, normalisation)
                all_lineouts.append(lineout)

            all_lineouts = np.asarray(all_lineouts)

            results[shot_type] = ProfileCamGroup(
                shot_numbers = shots_list,
                processed_images = all_images,
                lineouts = all_lineouts,
                lineout_mean = np.mean(all_lineouts, axis=0),
                lineout_stderr = np.std(all_lineouts, axis=0, ddof=1) / np.sqrt(len(all_lineouts))
            )

        return results