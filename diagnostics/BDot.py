import matplotlib.pyplot as plt
import numpy as np
from LAMP.diagnostic import Diagnostic


class BDot(Diagnostic):

    __version__ = 0.2
    __authors__ = ['Brendan Kettle', 'Margarida Pereira']
    __requirements__ = 'cv2'
    data_type = 'scope'

    def __init__(self, exp_obj, config_filepath):
        self.data_type = config_filepath['data_type']
        super().__init__(exp_obj, config_filepath)
        self._scope_cache = {}

    # ------------------------------------------------------------------
    # Caching
    # ------------------------------------------------------------------

    def get_scope_data(self, shot_dict):
        """
        Get scope data from the DAQ.
        Supports:
          - 'filename'
          - 'timestamp'
          - 'timeframe' (list of [start, end])
        Uses caching to avoid reloading the same data.
        """
    
        # Create cache key
        cache_key = tuple(
            (k, tuple(v) if isinstance(v, list) else v)
            for k, v in sorted(shot_dict.items())
        )
        if cache_key in self._scope_cache:
            print(f"[Cache] Using cached data for {self.config['name']}")
            return self._scope_cache[cache_key]
    
        # -------------------------------
        # Handle timeframe separately
        # -------------------------------
        if 'timeframe' in shot_dict:
            # Convert timeframe to a list of shot_dicts using DAQ
            shot_dict_list = self.DAQ.timeframe_to_shotdict(self.config['name'], shot_dict)
    
            if not shot_dict_list:
                print(f"[INFO] No files found in timeframe {shot_dict['timeframe']} for {self.config['name']}")
                return None
    
            # Load all files in that timeframe
            shot_data_list = []
            for sd in shot_dict_list:
                data = self.DAQ.get_shot_data(self.config['name'], sd)
                # unwrap if returned dict contains 'data'
                if isinstance(data, dict) and 'data' in data:
                    data = data['data']
                shot_data_list.append(data)
    
            self._scope_cache[cache_key] = shot_data_list
            return shot_data_list
    
        # -------------------------------
        # Otherwise, just use standard DAQ
        # -------------------------------
        else:
            shot_data = self.DAQ.get_shot_data(
                self.config['name'],
                shot_dict
            )
    
            if shot_data is None:
                print(f"[INFO] No data found for {self.config['name']} in shot {shot_dict}")
                return None
    
            if isinstance(shot_data, dict) and 'data' in shot_data:
                shot_data = shot_data['data']
    
            self._scope_cache[cache_key] = shot_data
            return shot_data

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    def _extract_voltages(self, shot_data, channels=None, subtract=None):
        """
        Extract voltage arrays from shot_data.
        Returns:
            voltages (stacked array),
            channel_index (dict),
            channel_names (list)
        """

        if isinstance(shot_data, dict):
            shot_data = [shot_data]

        all_channel_names = shot_data[0]['channel_names']
        channel_index = {name: i for i, name in enumerate(all_channel_names)}

        if subtract:
            chA, chB = subtract
            if chA not in channel_index or chB not in channel_index:
                raise ValueError(f"Invalid channel names: {chA}, {chB}")
            idxA = channel_index[chA]
            idxB = channel_index[chB]
        else:
            if channels is None:
                channels = all_channel_names
            for ch in channels:
                if ch not in channel_index:
                    raise ValueError(f"{ch} not in data: {all_channel_names}")
            idxs = [channel_index[ch] for ch in channels]

        voltages = []

        for shot in shot_data:
            chans = shot['channels']

            if subtract:
                v = chans[:, idxA] - chans[:, idxB]
            else:
                if len(idxs) > 1:
                    v = chans[:, idxs]
                else:
                    v = chans[:, idxs[0]]

            voltages.append(v)

        voltages = np.stack(voltages, axis=0)

        return voltages, channel_index, all_channel_names

    # ------------------------------------------------------------------
    # Time-domain plotting
    # ------------------------------------------------------------------

    def plot_scope(self,
                   shot_dict,
                   channels=None,
                   subtract=None,
                   average=False,
                   show_error=True,
                   fft=False,
                   title=None,
                   xmin=None,
                   xmax=None,
                   ymin=None,
                   ymax=None):

        shot_data = self.get_scope_data(shot_dict)
        if isinstance(shot_data, dict):
            shot_data = [shot_data]

        times = [shot['time'] for shot in shot_data]

        if average:
            time_ref = times[0]
            for t in times[1:]:
                if not np.allclose(t, time_ref):
                    raise ValueError("Time arrays differ between shots; cannot average.")
            time = time_ref
        else:
            time = times[0]

        voltages, channel_index, all_channel_names = \
            self._extract_voltages(shot_data, channels, subtract)

        if channels is None and not subtract:
            channels = all_channel_names

        if fft:
            x_t, voltages = self._compute_fft(voltages, shot_data)
        else:
            x_t = time

        fig, ax = plt.subplots(figsize=(10, 5))

                # Determine alpha based on number of shots
        alpha_val = 1.0 if len(voltages) == 1 else 0.75
        
        if average:
            voltage_means = np.mean(voltages, axis=0)
            if show_error:
                voltage_stds = np.std(voltages, axis=0)
        
            if voltages.ndim == 3:
                for i, ch in enumerate(channels):
                    ax.plot(x_t, voltage_means[:, i],
                            label=f'{ch} mean', zorder=3, alpha=0.8)
        
                    if show_error:
                        ax.plot(x_t, voltage_means[:, i] + voltage_stds[:, i],
                                '--', zorder=1, alpha=0.75, label=f'{ch} +1σ')
                        ax.plot(x_t, voltage_means[:, i] - voltage_stds[:, i],
                                '--', zorder=1, alpha=0.75, label=f'{ch} -1σ')
            else:
                ax.plot(x_t, voltage_means, label='mean', zorder=3)
        
                if show_error:
                    ax.plot(x_t, voltage_means + voltage_stds, '--', zorder=1, label=f'+1σ')
                    ax.plot(x_t, voltage_means - voltage_stds, '--', zorder=1, label=f'-1σ')
        
        else:
            # Single loop handles both 2D and 3D voltages
            for i, v in enumerate(voltages):
                if voltages.ndim == 3:
                    for j, ch in enumerate(channels):
                        ax.plot(x_t, v[:, j], label=f'Shot {i} - {ch}', alpha=alpha_val)
                else:
                    ax.plot(x_t, v, label=f'Shot {i}', alpha=alpha_val)

        if fft:
            ax.set_xlabel("Frequency [Hz]")
            ax.set_ylabel("Amplitude")
        else:
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Voltage [V]")

        # ----- Automatic title -----
        if title is None:
            scope_name = self.config['name']
            label_names = shot_data[0]['label_names']

            if subtract:
                chA, chB = subtract
                title = (
                    f"{scope_name}: "
                    f"{chA} ({label_names[channel_index[chA]]}) - "
                    f"{chB} ({label_names[channel_index[chB]]})"
                )
            else:
                ch_descs = [
                    f"{ch} ({label_names[channel_index[ch]]})"
                    for ch in channels
                ]
                title = f"{scope_name}: " + ", ".join(ch_descs)

            if average:
                title += " (averaged)"

        if fft:
            title = "FFT - " + title

        ax.set_title(title)

        if xmin is not None or xmax is not None:
            ax.set_xlim(left=xmin, right=xmax)

        if ymin is not None or ymax is not None:
            ax.set_ylim(bottom=ymin, top=ymax)

        ax.legend()
        fig.tight_layout()
        plt.show()


    def _compute_fft(self, voltages, shot_data):
        N = shot_data[0]['N']
        dt = shot_data[0]['dt']
    
        freqs = np.fft.rfftfreq(N, dt)
        fft_vals = np.abs(np.fft.rfft(voltages, axis=1))
    
        return freqs, fft_vals
    