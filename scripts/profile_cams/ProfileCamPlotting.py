import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# typing imports
from typing import Dict

from ProfileCamGroup import ProfileCamGroup
from ProfileCamAnalysis import ROI


def plot_group_overview(group: ProfileCamGroup, roi: ROI):
    images = group.processed_images
    lineouts = group.lineouts

    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, len(images), height_ratios=[1, 5], figure=fig)

    for i, img in enumerate(images):
        ax = fig.add_subplot(gs[0, i])

        ax.imshow(img, cmap="jet", vmax=1200)
        ax.set_xticks([])
        ax.set_yticks([])

        roi.add_to_axis(ax)

        ax.set_title(group.shot_numbers[i])

    ax_lineouts = fig.add_subplot(gs[1, :])
    xs = np.arange(lineouts.shape[1])

    for lineout in lineouts:
        ax_lineouts.plot(xs, lineout)

    ax_lineouts.set_xlabel("pixel")
    ax_lineouts.set_ylabel("intensity")

    plt.show()


def plot_group_comparison(groups: Dict[str, ProfileCamGroup]):

    fig,ax = plt.subplots(figsize=(8,5))

    for name, group in groups.items():
        xs = np.arange(group.lineout_mean.size)
        mean = group.lineout_mean
        stderr = group.lineout_stderr

        ax.plot(xs, mean, label=name)
        ax.fill_between(xs, mean-stderr, mean+stderr, alpha=0.3)

    ax.set_xlabel("Pixel")
    ax.set_ylabel("Intensity")
    ax.legend()
    plt.show()