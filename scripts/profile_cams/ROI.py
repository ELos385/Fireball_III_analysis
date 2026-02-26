import numpy as np
from matplotlib.patches import Rectangle

# typing imports
from abc import ABC, abstractmethod
from numpy.typing import NDArray

class ROI(ABC):
    @abstractmethod
    def apply(self, img: NDArray[float]) -> NDArray[float]:
        """return img cropped around ROI"""
        pass

    @abstractmethod
    def lineout(self, img: NDArray[float]) -> NDArray[float]:
        """return lineout inside ROI"""
        pass

    @abstractmethod
    def add_to_axis(self, ax):
        """draws ROI as an overlay on a matplotlib axis"""
        pass


class RectangleROI(ROI):
    def __init__(self, x0: int, x1: int, y0: int, y1: int):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1

    def apply(self, img: NDArray[float]) -> NDArray[float]:
        return img[self.y0:self.y1, self.x0:self.x1]

    def lineout(self, img: NDArray[float], axis: int = 1) -> NDArray[float]:
        roi_img = self.apply(img)
        return np.mean(roi_img, axis=axis)

    def add_to_axis(self, ax):
        rect = Rectangle(
            (self.x0, self.y0),
            self.x1 - self.x0,
            self.y1 - self.y0,
            edgecolor="red",
            facecolor="none",
            linewidth=2,
        )
        ax.add_patch(rect)