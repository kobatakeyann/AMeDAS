import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from config.figure.figure import COLOR_MAP, MAX_VALUE, MIN_VALUE


def get_color_from_value(value: float):
    cmap = plt.get_cmap(COLOR_MAP)
    norm = mcolors.Normalize(vmin=MIN_VALUE, vmax=MAX_VALUE)
    return cmap(norm(value))
