import matplotlib.pyplot as plt
import numpy as np

from LAMP.diagnostic import Diagnostic
from LAMP.utils.image_proc import ImageProc
from LAMP.utils.general import dict_update, mindex
from LAMP.utils.plotting import *



class ProfileCam_(Diagnostic):
    """
    Profile cams are HRM3 and HRM4
    """

    __version = 0.1
    __authors = ["Bryn Lloyd"]
    __requirements = 'cv2'
    data_type = 'csv'

    def __init__(self, exp_obj, config_filepath):
        """Initiate parent base Diagnostic class to get all shared attributes and funcs"""
        super().__init__(exp_obj, config_filepath)
        return

    def get_proc_shot(self, shot_dict, calib_id=None, debug=False):
        """
        Return a processed shot using saved or passed calibrations.
        Wraps base diagnostic class function.
        """
        img, x, y = super().get_proc_shot(shot_dict, calib_id=calib_id, debug=debug)
        if img is None:
            return None, None, None

        return img, x, y


    def plot_proc_shot(self, shot_dict, calib_id=None, vmin=None, vmax=None, colormap='plasma', debug=False):

        img, x, y = self.get_proc_shot(shot_dict, calib_id=calib_id, debug=debug)

        if vmin is None:
            vmin = np.nanmin(img)
        if vmax is None:
            vmax = np.percentile(img,99)


        fig,ax = plt.subplots()
        im = ax.imshow(img, vmin=vmin, vmax=vmax, cmap=get_colormap(colormap))
        cb = plt.colorbar(im)
        plt.title(self.shot_string(shot_dict))

        return fig,ax