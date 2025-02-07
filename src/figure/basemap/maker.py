import matplotlib.style as mplstyle
from cartopy.mpl.geoaxes import GeoAxes

from config.figure.base_map import (
    LAT_BOTTOM,
    LAT_TICK_INTERVAL,
    LAT_TOP,
    LON_LEFT,
    LON_RIGHT,
    LON_TICK_INTERVAL,
    deg_min_ticks,
    elevation_contour,
    elevation_shade,
    grid_line,
)
from config.figure.elevation_map import ZOOM_LEVEL
from figure.basemap.helper.type import RectangleArea
from figure.basemap.methods import Basemap


def make_base_map(ax: GeoAxes) -> GeoAxes:
    mplstyle.use("fast")
    print("Now making base map…", end="")
    basemap_ax = Basemap(
        ax=ax,
        area_range=RectangleArea(
            lon_left=LON_LEFT,
            lon_right=LON_RIGHT,
            lat_bottom=LAT_BOTTOM,
            lat_top=LAT_TOP,
        ),
    )
    basemap_ax.plot_coastline()
    basemap_ax.plot_prefecture_borders()
    basemap_ax.set_ticks(LON_TICK_INTERVAL, LAT_TICK_INTERVAL)
    basemap_ax.paint_sea()
    if elevation_shade:
        basemap_ax.plot_elevation_with_shading(zoom_level=ZOOM_LEVEL)
    if elevation_contour:
        basemap_ax.plot_elevation_with_contour(zoom_level=ZOOM_LEVEL)
    if grid_line:
        basemap_ax.draw_gridlines()
    if deg_min_ticks:
        basemap_ax.to_deg_min_ticks()
    basemap_ax.narrow_down_the_plot_area(
        LON_LEFT, LON_RIGHT, LAT_BOTTOM, LAT_TOP
    )
    print(" done!")
    return basemap_ax.ax
