import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
import re
from LAMP.diagnostic import Diagnostic
from LAMP.utils.image_proc import ImageProc
from LAMP.utils.general import dict_update, mindex
from LAMP.utils.plotting import *

class BDot(Diagnostic):

    __version = 0.1
    __authors = ['Brendan Kettle']
    __requirements = 'cv2'
    data_type = 'scope'


    def __init__(self, exp_obj, config_filepath):
        """Initiate parent base Diagnostic class to get all shared attributes and funcs"""
        self.data_type = config_filepath['data_type']
        super().__init__(exp_obj, config_filepath)
        return

    def get_scope_data(self, shot_dict):
        return self.DAQ.get_shot_data(self.config['name'], shot_dict)
    