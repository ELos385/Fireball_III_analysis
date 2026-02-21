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


    def plot_scope(self, shot_data, 
                    channels=None,        # list of channel names to plot
                    subtract=None,        # tuple of two channel names to subtract: (A, B)
                    average=False,        # if True, average over multiple shots
                    show_error=True,      # plot ±1 sigma if averaging
                    title=None):

        """
        Plot Bdot waveform data with optional averaging and channel subtraction.

        Parameters
        ----------
        shot_data : list of dicts
            Output of get_scope_data().
        channels : list of str
            Channels to plot (default: all).
        subtract : tuple of str
            Plot channel[0] - channel[1] if specified.
        average : bool
            Average over multiple shots.
        show_error : bool
            Show ±1σ error bands when averaging.
        title : str
            Optional plot title.
        """
        # Ensure shot_data is always a list
        if isinstance(shot_data, dict):
            shot_data = [shot_data]
        
        # --- Determine channels to use ---
        all_channel_names = shot_data[0]['channel_names']
        if subtract:
            chA, chB = subtract
            if chA not in all_channel_names or chB not in all_channel_names:
                raise ValueError(f"Channels {chA} or {chB} not in data: {all_channel_names}")
        else:
            if channels is None:
                channels = all_channel_names
            for ch in channels:
                if ch not in all_channel_names:
                    raise ValueError(f"Channel {ch} not in data: {all_channel_names}")

        # --- Prepare data ---
        times = [shot['time'] for shot in shot_data]

        # All times must be identical for averaging
        if average:
            time_ref = times[0]
            for t in times[1:]:
                if not np.allclose(t, time_ref):
                    raise ValueError("Time arrays differ between shots; cannot average.")
            time = time_ref
        else:
            time = times[0]

        # --- Build voltage arrays ---
        voltages = []
        for shot in shot_data:
            chans = shot['channels']
            if subtract:
                idxA = all_channel_names.index(chA)
                idxB = all_channel_names.index(chB)
                v = chans[:, idxA] - chans[:, idxB]
            else:
                # Stack selected channels horizontally
                idxs = [all_channel_names.index(ch) for ch in channels]
                v = chans[:, idxs] if len(idxs) > 1 else chans[:, idxs[0]]
            voltages.append(v)
        voltages = np.array(voltages)  # shape: (n_shots, n_samples, n_channels) or (n_shots, n_samples)

        # --- Plot ---
        plt.figure(figsize=(10, 5))

        if average:
            voltage_means = np.mean(voltages, axis=0)
            voltage_stds = np.std(voltages, axis=0)

            if voltages.ndim == 3:
                # multiple channels
                for i, ch in enumerate(channels):
                    plt.plot(time, voltage_means[:, i], label=f'{ch} mean', zorder=3)
                    if show_error:
                        upp_bound = voltage_means[:, i] + voltage_stds[:, i]
                        low_bound = voltage_means[:, i] - voltage_stds[:, i]
                        plt.plot(time, upp_bound, '--', label='+1σ', zorder=1)
                        plt.plot(time, low_bound, '--', label='-1σ', zorder=1)
            else:
                # single channel or subtraction
                plt.plot(time, voltage_means, label='mean', zorder=3)
                if show_error:
                    upp_bound = voltage_means + voltage_stds
                    low_bound = voltage_means - voltage_stds
                    plt.plot(time, upp_bound, '--', label='+1σ', zorder=1)
                    plt.plot(time, low_bound, '--', label='-1σ', zorder=1)

        else:
            # plot each shot individually
            for i, v in enumerate(voltages):
                if voltages.ndim == 3:
                    for j, ch in enumerate(channels):
                        plt.plot(time, v[:, j], label=f'Shot {i} - {ch}')
                else:
                    plt.plot(time, v, label=f'Shot {i}')

        plt.xlabel('Time [s]')
        plt.ylabel('Voltage [V]')
        if title:
            plt.title(title)
        plt.legend()
        plt.tight_layout()
        plt.show()