
import os
#from configparser import ConfigParser, ExtendedInterpolation
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import ndimage
from skimage.morphology import reconstruction
import re
from LAMP.utils.io import *
from LAMP.utils.general import dict_update
from LAMP.utils.image_proc import ImageProc
from LAMP.utils.plotting import plot_montage
from LAMP.utils.plotting import get_colormap
from LAMP.diagnostic import Diagnostic


class Template(Diagnostic):
    """Base class for Diagnostics. 
    Currently this mostly handles loading/saving calibrations.
    """

    # Diagnostics attributes

    def __init__(self, exp_obj, config_filepath):
        """Initiate parent base Diagnostic class to get all shared attributes and funcs"""
        self.data_type = config_filepath['data_type'] # This is needed for __init__ of Diagnostic
        super().__init__(exp_obj, config_filepath)
        return
