import numpy as np
from matplotlib.patches import Rectangle, Wedge
from skimage.transform import warp_polar
from scipy.ndimage import affine_transform

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

class RotatedRectangleROI(ROI):
    def __init__(self, x0: int, x1: int, y0: int, y1: int, cx: float, cy: float, angle: float):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.cx = cx
        self.cy = cy
        self.angle = angle

    def _rotate_about_point(self, img: NDArray[float]) -> NDArray[float]:
        theta = np.deg2rad(self.angle)

        cos_t = np.cos(theta)
        sin_t = np.sin(theta)

        # Forward rotation matrix
        R = np.array([
            [cos_t, -sin_t],
            [sin_t,  cos_t]
        ])

        # affine_transform needs inverse
        R_inv = R.T

        # Compute offset so rotation is about (cx, cy)
        c = np.array([self.cy, self.cx])  # row, col order

        offset = c - R_inv @ c

        rotated = affine_transform(
            img,
            R_inv,
            offset=offset,
            order=1,
            mode="constant",
            cval=0.0,
        )

        return rotated


    def apply(self, img: NDArray[float]) -> NDArray[float]:
        rotated = self._rotate_about_point(img)
        return rotated[self.y0:self.y1, self.x0:self.x1]

    def lineout(self, img: NDArray[float], axis: int = 1) -> NDArray[float]:
        roi_img = self.apply(img)
        return np.mean(roi_img, axis=axis)



    def add_to_axis(self, ax):
        from matplotlib.patches import Rectangle
        from matplotlib.transforms import Affine2D

        rect = Rectangle(
            (self.x0, self.y0),
            self.x1 - self.x0,
            self.y1 - self.y0,
            edgecolor="red",
            facecolor="none",
            linewidth=2,
        )

        transform = (
            Affine2D()
            .rotate_deg_around(self.cx, self.cy, self.angle)
            + ax.transData
        )

        rect.set_transform(transform)
        ax.add_patch(rect)



class SectorROI(ROI):
    def __init__(self, cx: int, cy: int, radius: int, theta0: int, dtheta: int):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.theta0 = theta0
        self.dtheta = dtheta


    def _to_polar(self, img: NDArray[float]) -> NDArray[float]:
        polar = warp_polar(
            img,
            center = (self.cy, self.cx),
            radius = self.radius,
            output_shape = (360, self.radius),
        )
        return polar

    def apply(self, img: NDArray[float]) -> NDArray[float]:
        polar = self._to_polar(img)

        if self.dtheta >= 360:
            return polar
        
        theta_start = self.theta0 % 360
        theta_end = (self.theta0 + self.dtheta) % 360
        if theta_start < theta_end:
            sector = polar[theta_start:theta_end]
        else: # wraparound
            sector = np.vstack((
                polar[theta_start:],
                polar[:theta_end]
            ))    

        return sector


    def lineout(self, img: NDArray[float]) -> NDArray[float]:
        sector = self.apply(img)
        return np.mean(sector, axis=0)

    def add_to_axis(self, ax):
        wedge = Wedge(
            center=(self.cx, self.cy),
            r=self.radius,
            theta1=self.theta0,
            theta2=self.theta0 + self.dtheta,
            edgecolor="red",
            facecolor="none",
            linewidth=2,
        )
        ax.add_patch(wedge)
        