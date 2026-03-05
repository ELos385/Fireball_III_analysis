import numpy as np
import matplotlib.pyplot as plt


# ------------------------------------------------------------------
# Internal helper
# ------------------------------------------------------------------

def _extract_cross_voltages(scopeA, scopeB, shot_dict, chA, chB):

    dataA = scopeA.get_scope_data(shot_dict)
    dataB = scopeB.get_scope_data(shot_dict)

    if isinstance(dataA, dict):
        dataA = [dataA]
    if isinstance(dataB, dict):
        dataB = [dataB]

    if len(dataA) != len(dataB):
        raise ValueError("Different number of shots between scopes.")

    channel_index_A = {
        name: i for i, name in enumerate(dataA[0]['channel_names'])
    }
    channel_index_B = {
        name: i for i, name in enumerate(dataB[0]['channel_names'])
    }

    if chA not in channel_index_A:
        raise ValueError(f"{chA} not in {scopeA.config['name']}")
    if chB not in channel_index_B:
        raise ValueError(f"{chB} not in {scopeB.config['name']}")

    idxA = channel_index_A[chA]
    idxB = channel_index_B[chB]

    dtA = dataA[0]['dt']
    dtB = dataB[0]['dt']

    if not np.isclose(dtA, dtB):
        raise ValueError("Scopes have different dt values; cannot align without interpolation.")

    dt = dtA 

    # Determine overlapping time range
    t_start = max(dataA[0]['time'][0], dataB[0]['time'][0])
    t_end   = min(dataA[0]['time'][-1], dataB[0]['time'][-1])

    # Compute indices for the overlap
    def overlap_indices(time_array):
        start_idx = int(round((t_start - time_array[0]) / dt))
        end_idx   = int(round((t_end - time_array[0]) / dt)) + 1
        return start_idx, end_idx

    idx_start_A, idx_end_A = overlap_indices(dataA[0]['time'])
    idx_start_B, idx_end_B = overlap_indices(dataB[0]['time'])

    time_common = dataA[0]['time'][idx_start_A:idx_end_A]

    result = []
    for shotA, shotB in zip(dataA, dataB):

        vA = shotA['channels'][:, idxA][idx_start_A:idx_end_A]
        vB = shotB['channels'][:, idxB][idx_start_B:idx_end_B]

        result.append(vA - vB)

    result = np.stack(result, axis=0)

    return result, time_common, dt, dataA, dataB


# ------------------------------------------------------------------
# Time-domain
# ------------------------------------------------------------------

def plot_cross_scope(scopeA,
                     scopeB,
                     shot_dict,
                     chA,
                     chB,
                     fft=False,
                     average=False,
                     show_error=True,
                     title=None,
                     xmin=None,
                     xmax=None,
                     ymin=None,
                     ymax=None,
                     fmax=None):

        signals, time, dt, dataA, dataB = \
            _extract_cross_voltages(scopeA, scopeB, shot_dict, chA, chB)
    
        fig, ax = plt.subplots(figsize=(10,5))
    
        # -----------------------------
        # FFT branch
        # -----------------------------
        if fft:
    
            signals, x = _compute_fft(signals, dt)
    
            if fmax is not None:
                mask = x <= fmax
                x = x[mask]
                signals = signals[:, mask]
    
            xlabel = "Frequency [Hz]"
            ylabel = "Amplitude"
    
        # -----------------------------
        # Time domain branch
        # -----------------------------
        else:
    
            x = time
            xlabel = "Time [s]"
            ylabel = "Voltage [V]"
    
        alpha_val = 1.0 if len(signals) == 1 else 0.75
    
        if average:
    
            mean = np.mean(signals, axis=0)
            ax.plot(x, mean, label="mean", zorder=3)
    
            if show_error:
                std = np.std(signals, axis=0)
                ax.plot(x, mean + std, "--", zorder=1)
                ax.plot(x, mean - std, "--", zorder=1)
    
        else:
    
            for i, v in enumerate(signals):
                ax.plot(x, v, label=f"Shot {i}", alpha=alpha_val)
    
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
        # -----------------------------
        # Title formatting
        # -----------------------------
        if title is None:
    
            scopeA_name = scopeA.config['name']
            scopeB_name = scopeB.config['name']
    
            labelA = dataA[0]['label_names'][dataA[0]['channel_names'].index(chA)]
            labelB = dataB[0]['label_names'][dataB[0]['channel_names'].index(chB)]
    
            prefix = "FFT - " if fft else ""
    
            title = (
                f"{prefix}{scopeA_name}: {chA} ({labelA}) - "
                f"{scopeB_name}: {chB} ({labelB})"
            )
    
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

def _compute_fft(signals, dt):

    N = signals.shape[1]   # actual signal length
    freqs = np.fft.rfftfreq(N, dt)

    fft_vals = np.abs(np.fft.rfft(signals, axis=1))

    return fft_vals, freqs


