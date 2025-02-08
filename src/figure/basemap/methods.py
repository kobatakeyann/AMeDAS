import cartopy.crs as ccrs
import cartopy.io.shapereader as shapereader
import matplotlib.pyplot as plt
from cartopy.feature import NaturalEarthFeature
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1 import make_axes_locatable

from config.figure.base_map import GRIDLINE_COLOR, GRIDLINE_WIDTH
from config.figure.elevation_map import (
    CONTOUR_COLOR,
    CONTOUR_LABEL_SIZE,
    CONTOUR_WIDTH,
    HEIGHT_MAX,
)
from elevation.meshdata import Elevation
from figure.basemap.helper.level_calculation import (
    get_clabel_levels,
    get_contour_levels,
    get_shade_levels,
)
from figure.basemap.helper.ticks_formatter import (
    format_lat_ticks,
    format_lon_ticks,
)
from figure.basemap.helper.ticks_setter import TicksLocator
from figure.basemap.helper.type import RectangleArea


class Basemap:
    def __init__(self, ax: GeoAxes, area_range: RectangleArea) -> None:
        self.ax = ax
        self._area_range = area_range

    def plot_coastline(self) -> None:
        self.ax.coastlines(linewidths=1, resolution="10m")

    def plot_prefecture_borders(self) -> None:
        shpfilename = shapereader.natural_earth(
            resolution="10m",
            category="cultural",
            name="admin_1_states_provinces",
        )
        provinces = shapereader.Reader(shpfilename).records()
        prefs = filter(
            lambda province: province.attributes["admin"] == "Japan", provinces
        )
        for pref in prefs:
            geometry = pref.geometry
            self.ax.add_geometries(
                [geometry],
                ccrs.PlateCarree(),
                facecolor="none",
                linestyle="-",
                linewidth=0.1,
            )

    def paint_sea(self) -> None:
        self.ax.add_feature(
            NaturalEarthFeature(
                "physical",
                "ocean",
                "10m",
                facecolor="lightblue",
                edgecolor="black",
                linewidth=0.2,
            ),
        )

    def paint_land(self) -> None:
        self.ax.add_feature(
            NaturalEarthFeature(
                "physical",
                "land",
                "10m",
                facecolor="lightgreen",
                edgecolor="black",
                alpha=0.6,
                linewidth=0.2,
                zorder=0,
            ),
        )

    def plot_elevation_with_shading(self, zoom_level: int) -> None:
        gpv_fetcher = Elevation(
            lon_left=self._area_range.lon_left,
            lon_right=self._area_range.lon_right,
            lat_bottom=self._area_range.lat_bottom,
            lat_top=self._area_range.lat_top,
            zoom_level=zoom_level,
        )
        elevation_array = gpv_fetcher.get_concatted_array()
        lon_coords, lat_coords = gpv_fetcher.get_coordinates_for_plot()
        cmap = plt.get_cmap("YlOrRd")
        cmap.set_under("white")
        shade = self.ax.contourf(
            lon_coords,
            lat_coords,
            elevation_array,
            alpha=0.7,
            transform=ccrs.PlateCarree(),
            cmap=cmap,
            levels=get_shade_levels(),
            extend="max",
        )
        shade.set_clim(vmin=150, vmax=HEIGHT_MAX)
        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes("right", size="5%", pad=0.2, axes_class=Axes)
        cbar = plt.colorbar(
            shade,
            cax=cax,
            orientation="vertical",
        )
        cbar.set_label("[m]", y=1.07, rotation=0, fontsize=12)

    def plot_elevation_with_contour(
        self,
        zoom_level: int,
        is_labeled_contour: bool = False,
    ) -> None:
        gpv_fetcher = Elevation(
            lon_left=self._area_range.lon_left,
            lon_right=self._area_range.lon_right,
            lat_bottom=self._area_range.lat_bottom,
            lat_top=self._area_range.lat_top,
            zoom_level=zoom_level,
        )
        elevation_array = gpv_fetcher.get_concatted_array()
        lon_coords, lat_coords = gpv_fetcher.get_coordinates_for_plot()
        self.contours = self.ax.contour(
            lon_coords,
            lat_coords,
            elevation_array,
            transform=ccrs.PlateCarree(),
            levels=get_contour_levels(),
            linewidths=CONTOUR_WIDTH,
            colors=CONTOUR_COLOR,
        )
        if is_labeled_contour:
            self.ax.clabel(
                self.contours,
                levels=get_clabel_levels(),
                fmt="%.{0[0]}f".format([0]),
                fontsize=CONTOUR_LABEL_SIZE,
            )

    def draw_gridlines(self) -> None:
        gl = self.ax.gridlines(
            draw_labels=True, color=GRIDLINE_COLOR, linewidth=GRIDLINE_WIDTH
        )
        gl.right_labels = False
        gl.top_labels = False
        gl.left_labels = False
        gl.bottom_labels = False

    def set_ticks(self, lon_interval: float, lat_interval: float) -> None:
        ticks_locator = TicksLocator(lon_interval, lat_interval)
        self.ax.set_xticks(ticks_locator.xloc, crs=ccrs.PlateCarree())
        self.ax.set_yticks(ticks_locator.yloc, crs=ccrs.PlateCarree())
        self.ax.xaxis.set_major_formatter(LongitudeFormatter())
        self.ax.yaxis.set_major_formatter(LatitudeFormatter())

    def to_deg_min_ticks(self) -> None:
        self.ax.xaxis.set_major_formatter(format_lon_ticks)
        self.ax.yaxis.set_major_formatter(format_lat_ticks)

    def narrow_down_the_plot_area(
        self,
        lon_left: float,
        lon_right: float,
        lat_bottom: float,
        lat_top: float,
    ) -> None:
        self.ax.set_extent(
            (lon_left, lon_right, lat_bottom, lat_top), ccrs.PlateCarree()
        )
