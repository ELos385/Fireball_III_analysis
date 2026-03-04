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

        cache_key = tuple(
            (k, tuple(v) if isinstance(v, list) else v)
            for k, v in sorted(shot_dict.items())
        )

        if cache_key in self._scope_cache:
            print(f"[Cache] Using cached data for {self.config['name']}")
            return self._scope_cache[cache_key]

        shot_data = self.DAQ.get_shot_data(
            self.config['name'],
            shot_dict
        )

        if shot_data is None:
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

        fig, ax = plt.subplots(figsize=(10, 5))

        if average:
            voltage_means = np.mean(voltages, axis=0)
            if show_error:
                voltage_stds = np.std(voltages, axis=0)

            if voltages.ndim == 3:
                for i, ch in enumerate(channels):
                    ax.plot(time, voltage_means[:, i],
                            label=f'{ch} mean', zorder=3, alpha=0.8)

                    if show_error:
                        ax.plot(time, voltage_means[:, i] + voltage_stds[:, i],
                                '--', zorder=1, alpha=0.75)
                        ax.plot(time, voltage_means[:, i] - voltage_stds[:, i],
                                '--', zorder=1, alpha=0.75)
            else:
                ax.plot(time, voltage_means, label='mean', zorder=3)

                if show_error:
                    ax.plot(time, voltage_means + voltage_stds, '--', zorder=1)
                    ax.plot(time, voltage_means - voltage_stds, '--', zorder=1)

        else:
            for i, v in enumerate(voltages):
                if voltages.ndim == 3:
                    for j, ch in enumerate(channels):
                        ax.plot(time, v[:, j],
                                label=f'Shot {i} - {ch}', alpha=0.75)
                else:
                    ax.plot(time, v,
                            label=f'Shot {i}', alpha=0.75)

        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Voltage [V]')

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

        ax.set_title(title)

        if xmin is not None or xmax is not None:
            ax.set_xlim(left=xmin, right=xmax)

        if ymin is not None or ymax is not None:
            ax.set_ylim(bottom=ymin, top=ymax)

        ax.legend()
        fig.tight_layout()
        plt.show()

    # ------------------------------------------------------------------
    # Frequency-domain plotting
    # ------------------------------------------------------------------

    def plot_fft(self,
                 shot_dict,
                 channels=None,
                 subtract=None,
                 average=False,
                 show_error=True,
                 title=None,
                 fmax=None):

        shot_data = self.get_scope_data(shot_dict)
        if isinstance(shot_data, dict):
            shot_data = [shot_data]

        voltages, channel_index, all_channel_names = \
            self._extract_voltages(shot_data, channels, subtract)

        N = shot_data[0]['N']
        dt = shot_data[0]['dt']
        freqs = np.fft.rfftfreq(N, dt)

        fig, ax = plt.subplots(figsize=(10, 5))

        if average:
            fft_vals = np.abs(np.fft.rfft(voltages, axis=1))
            fft_mean = np.mean(fft_vals, axis=0)

            if show_error:
                fft_std = np.std(fft_vals, axis=0)

            if fft_vals.ndim == 3:
                for i, ch in enumerate(channels):
                    ax.plot(freqs, fft_mean[:, i],
                            linewidth=2, label=f'{ch} mean', zorder=3)

                    if show_error:
                        ax.plot(freqs, fft_mean[:, i] + fft_std[:, i], '--')
                        ax.plot(freqs, fft_mean[:, i] - fft_std[:, i], '--')
            else:
                ax.plot(freqs, fft_mean,
                        linewidth=2, label='Mean', zorder=3)

                if show_error:
                    ax.plot(freqs, fft_mean + fft_std, '--')
                    ax.plot(freqs, fft_mean - fft_std, '--')

        else:
            for i, v in enumerate(voltages):
                fft_val = np.abs(np.fft.rfft(v, axis=0))

                if fft_val.ndim == 2:
                    for j, ch in enumerate(channels):
                        ax.plot(freqs, fft_val[:, j],
                                label=f'Shot {i} - {ch}')
                else:
                    ax.plot(freqs, fft_val,
                            label=f'Shot {i}', alpha = 0.75)

        if fmax:
            ax.set_xlim(0, fmax)

        if title is None:
            scope_name = self.config['name']
            label_names = shot_data[0]['label_names']
            title = "FFT - "

            if subtract:
                chA, chB = subtract
                title += (
                    f"{scope_name}: "
                    f"{chA} ({label_names[channel_index[chA]]}) - "
                    f"{chB} ({label_names[channel_index[chB]]})"
                )
            else:
                ch_descs = [
                    f"{ch} ({label_names[channel_index[ch]]})"
                    for ch in channels
                ]
                title += f"{scope_name}: " + ", ".join(ch_descs)

            if average:
                title += " (averaged)"

        ax.set_title(title)
        ax.set_xlabel("Frequency [Hz]")
        ax.set_ylabel("Amplitude")
        ax.legend()
        fig.tight_layout()
        plt.show()