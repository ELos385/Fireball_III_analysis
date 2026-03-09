import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# typing imports
from typing import Dict

from ProfileCamGroup import ProfileCamGroup
from ProfileCamAnalysis import ROI


def plot_group_overview(group: ProfileCamGroup):
    images = group.processed_images
    lineouts = group.lineouts
    roi = group._roi

    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, len(images), height_ratios=[1, 5], figure=fig)

    # plot images with roi overlay
    for i, img in enumerate(images):
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(img, cmap="jet", vmax=1200)
        ax.set_xticks([])
        ax.set_yticks([])
        roi.add_to_axis(ax)
        ax.set_title(group.shot_numbers[i])

    ax_lineouts = fig.add_subplot(gs[1, :])
    pixels = np.arange(lineouts.shape[1])
    for lineout in lineouts:
        ax_lineouts.plot(pixels, lineout)
    ax_lineouts.set_xlim(pixels[0], pixels[-1])


    ax_lineouts.set_xlabel("pixel")
    ax_lineouts.set_ylabel("intensity")

    
    try:
        phys_axis = roi.lineout_axis(group.x, group.y)
    except NotImplementedError:
        print(f"ROI of type {type(roi)} does not support physical units... yet")
    else:
        xs, units = phys_axis.values, phys_axis.units
        ax_top = ax_lineouts.twiny()
        ax_top.set_xlim(xs[0], xs[-1])
        ax_top.set_xlabel(f"distance ({units})")

    plt.show()


def plot_group_comparison(groups: Dict[str, ProfileCamGroup]):

    fig,ax = plt.subplots(figsize=(8,5))

    for name, group in groups.items():
        pixels = np.arange(group.lineout_mean.size)
        mean = group.lineout_mean
        stderr = group.lineout_stderr

        ax.plot(pixels, mean, label=name)
        ax.fill_between(pixels, mean-stderr, mean+stderr, alpha=0.3)
    ax.set_xlim(pixels[0], pixels[-1])
    ax.set_xlabel("Pixel")
    ax.set_ylabel("Intensity")
    ax.legend()



    roi = next(iter(groups.values()))._roi
    try:
        phys_axis = roi.lineout_axis(group.x, group.y)
    except (NotImplementedError, AttributeError):
        print(f"ROI of type {type(roi)} does not support physical units... yet")
    else:
        xs, units = phys_axis.values, phys_axis.units
        ax_top = ax.twiny()
        ax_top.set_xlim(xs[0], xs[-1])
        ax_top.set_xlabel(f"distance ({units})")

    
    plt.show()