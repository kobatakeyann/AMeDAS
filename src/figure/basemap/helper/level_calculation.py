import numpy as np

from config.figure.elevation_map import (
    CONTOUR_LABEL_INTERVAL,
    HEIGHT_INTERVAL,
    HEIGHT_MAX,
    HEIGHT_MIN,
)


def get_contour_levels() -> np.ndarray:
    levels = np.arange(
        float(HEIGHT_MIN),
        float(HEIGHT_MAX) + 0.000000000000001,
        float(HEIGHT_INTERVAL),
    )
    return levels


def get_clabel_levels() -> np.ndarray:
    levels = np.arange(
        float(HEIGHT_MIN),
        float(HEIGHT_MAX) + 0.000000000000001,
        float(CONTOUR_LABEL_INTERVAL),
    )
    return levels
