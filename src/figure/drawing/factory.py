import pickle
from typing import cast

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.mpl.geoaxes import GeoAxes

from figure.basemap.helper.fig_size import calculate_figsize
from figure.basemap.maker import make_base_map


class FigureFactory:
    def __init__(self) -> None:
        fig = plt.figure(figsize=calculate_figsize())
        ax = cast(
            GeoAxes,
            fig.add_subplot(111, projection=ccrs.PlateCarree()),
        )
        make_base_map(ax)
        self._basefig = pickle.dumps(fig, protocol=pickle.HIGHEST_PROTOCOL)
