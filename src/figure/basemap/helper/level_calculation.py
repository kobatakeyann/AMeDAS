import numpy as np

from config.figure.elevation_map import HEIGHT_INTERVAL, HEIGHT_MAX, HEIGHT_MIN


def get_shade_levels() -> np.ndarray:
    levels = np.arange(
        float(HEIGHT_MIN),
        float(HEIGHT_MAX) + 0.000000000000001,
        float(HEIGHT_INTERVAL),
    )
    return levels


def get_contour_levels() -> np.ndarray:
    HEIGHT_MIN = 150
    levels = np.arange(
        HEIGHT_MIN,
        float(HEIGHT_MAX) + 0.000000000000001,
        float(HEIGHT_INTERVAL),
    )
    return levels
