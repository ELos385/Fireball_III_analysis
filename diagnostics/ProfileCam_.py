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

class ProfileCam_(Diagnostic):
    """
    Profile cams are HRM3 and HRM4
    """

    __version = 0.1
    __authors = ['Brendan Kettle', "Bryn Lloyd"]
    __requirements = 'cv2'
    data_type = 'csv'

    curr_img = None
    img_units = ['Counts']
    x_mm, y_mm = None, None
    x_mrad, y_mrad = None, None
    x_MeV, y_MeV = None, None

    def __init__(self, exp_obj, config_filepath):
        """Initiate parent base Diagnostic class to get all shared attributes and funcs"""
        super().__init__(exp_obj, config_filepath)
        return

    def get_proc_shot(self, shot_dict, calib_id=None, apply_disp=True, apply_div=True, apply_charge=True, roi_mm=None, roi_MeV=None, roi_mrad=None, debug=False):
        """
        Return a processed shot using saved or passed calibrations. (there is no calibration for this for now)
        Wraps base diagnostic class function, adding dispersion, divergence, charge.
        """

        # use diagnostic base function
        # loads calib id and run_img_calib for standard calibration routines
        # img, x, y = super().get_proc_shot(shot_dict, calib_id=calib_id, debug=debug)
        img, x, y = super().get_proc_shot(shot_dict, calib_id=None, debug=debug)
        if img is None:
            return None, None, None

        # ========================================
        # crop images around edge of Chromox screen
        # ik this should probably go in calib, but i cba
        # ========================================
        
        crop = None
        if self.config["name"] == "HRM3":
            crop = [215, 400, 50, 300]    # [xmin, xmax, ymin, ymax]
        elif self.config["name"] == "HRM4":
            crop = [180, 450, 0, 375]    # [xmin, xmax, ymin, ymax]
        else:
            print("what r u doing")

        if crop:
            img = img[crop[2] : crop[3], crop[0] : crop[1]]
            y, x = np.shape(img)
        
        return img, x, y




    def plot_proc_shot(self, shot_dict, calib_id=None, vmin=None, vmax=None, colormap='plasma', debug=False):
        """
        super().plot_proc_shot() actually just doesnt work so ill overwrite it
        """

        img, x, y = self.get_proc_shot(shot_dict, calib_id=calib_id, debug=debug)

        if vmin is None:
            vmin = np.nanmin(img)
        if vmax is None:
            #vmax = np.nanmax(img)
            vmax = np.percentile(img,99)


        fig,ax = plt.subplots(figsize=(10,10))
        im = ax.imshow(img, vmin=vmin, vmax=vmax, cmap=get_colormap(colormap))
        cb = plt.colorbar(im)
        plt.title(self.shot_string(shot_dict))
        plt.tight_layout()
        plt.show(block=False)

        return fig, plt.gca()
