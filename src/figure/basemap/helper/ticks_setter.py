import numpy as np


class TicksLocator:
    def __init__(self, lon_interval: float, lat_interval: float) -> None:
        self.xloc = np.arange(0, 180 + 0.00000001, lon_interval)
        self.yloc = np.arange(0, 90 + 0.00000001, lat_interval)
