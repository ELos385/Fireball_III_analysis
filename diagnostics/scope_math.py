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

    return result, time_common, dataA, dataB


# ------------------------------------------------------------------
# Time-domain
# ------------------------------------------------------------------

def plot_cross_scope(scopeA,
                     scopeB,
                     shot_dict,
                     chA,
                     chB,
                     average=False,
                     show_error=True,
                     title=None,
                     xmin=None,
                     xmax=None,
                     ymin=None,
                     ymax=None):

    result, time, dataA, dataB = \
        _extract_cross_voltages(scopeA, scopeB, shot_dict, chA, chB)

    fig, ax = plt.subplots(figsize=(10, 5))

    alpha_val = 1.0 if len(result) == 1 else 0.75

    if average:
        mean = np.mean(result, axis=0)

        ax.plot(time, mean, label="mean", zorder=3)

        if show_error:
            std = np.std(result, axis=0)
            ax.plot(time, mean + std, "--", zorder=1)
            ax.plot(time, mean - std, "--", zorder=1)

    else:
        for i, v in enumerate(result):
            ax.plot(time, v, label=f"Shot {i}", alpha=alpha_val)

    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Voltage [V]")

    # ---- Consistent title formatting ----
    if title is None:

        scopeA_name = scopeA.config['name']
        scopeB_name = scopeB.config['name']

        labelA = dataA[0]['label_names'][
            dataA[0]['channel_names'].index(chA)
        ]
        labelB = dataB[0]['label_names'][
            dataB[0]['channel_names'].index(chB)
        ]

        title = (
            f"{scopeA_name}: {chA} ({labelA}) - "
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


# ------------------------------------------------------------------
# Frequency-domain
# ------------------------------------------------------------------

def plot_cross_scope_fft(scopeA,
                         scopeB,
                         shot_dict,
                         chA,
                         chB,
                         average=False,
                         show_error=True,
                         title=None,
                         fmax=None):

    result, _, dataA, dataB = \
        _extract_cross_voltages(scopeA, scopeB, shot_dict, chA, chB)

    N = dataA[0]['N']
    dt = dataA[0]['dt']
    freqs = np.fft.rfftfreq(N, dt)

    fig, ax = plt.subplots(figsize=(10, 5))

    if average:
        fft_vals = np.abs(np.fft.rfft(result, axis=1))
        mean = np.mean(fft_vals, axis=0)

        ax.plot(freqs, mean, linewidth=2, label="mean", zorder=3)

        if show_error:
            std = np.std(fft_vals, axis=0)
            ax.plot(freqs, mean + std, "--")
            ax.plot(freqs, mean - std, "--")

    else:
        for i, v in enumerate(result):
            fft_val = np.abs(np.fft.rfft(v))
            ax.plot(freqs, fft_val, label=f"Shot {i}")

    if fmax:
        ax.set_xlim(0, fmax)

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Amplitude")

    # ---- Consistent title formatting ----
    if title is None:

        scopeA_name = scopeA.config['name']
        scopeB_name = scopeB.config['name']

        labelA = dataA[0]['label_names'][
            dataA[0]['channel_names'].index(chA)
        ]
        labelB = dataB[0]['label_names'][
            dataB[0]['channel_names'].index(chB)
        ]

        title = (
            f"FFT - {scopeA_name}: {chA} ({labelA}) - "
            f"{scopeB_name}: {chB} ({labelB})"
        )

        if average:
            title += " (averaged)"

    ax.set_title(title)

    ax.legend()
    fig.tight_layout()
    plt.show()