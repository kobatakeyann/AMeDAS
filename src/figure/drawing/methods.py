import os

import cartopy.crs as ccrs
from matplotlib.figure import Figure

from config.figure.figure import (
    DPI,
    TEXT_LABEL_SIZE,
    TITLE_SIZE,
    VECTOR_COLOR,
    VECTOR_LEDEND_VALUE,
    VECTOR_LEGEND_UNIT,
    VECTOR_REDUCTION_SCALE,
    VECTOR_WIDTH,
)
from figure.basemap.methods import GeoAxes


class PlotMethods:
    def __init__(self, ax: GeoAxes) -> None:
        self.ax = ax

    def plot_text_label(
        self, x_loc: float, y_loc: float, text: str, color
    ) -> None:
        self.ax.text(
            x_loc,
            y_loc,
            text,
            size=TEXT_LABEL_SIZE,
            color=color,
            transform=ccrs.PlateCarree(),
            horizontalalignment="center",
            verticalalignment="center",
            clip_on=True,
        )

    def plot_vector(
        self,
        lon: list[float],
        lat: list[float],
        u_component: list[float],
        v_component: list[float],
    ) -> None:
        self.vector = self.ax.quiver(
            lon,
            lat,
            u_component,
            v_component,
            zorder=3,
            transform=ccrs.PlateCarree(),
            angles="xy",
            scale_units="xy",
            color=VECTOR_COLOR,
            scale=VECTOR_REDUCTION_SCALE,
            width=VECTOR_WIDTH,
        )

    def plot_legend_vector(self) -> None:
        self.ax.quiverkey(
            self.vector,
            0.92,
            -0.08,
            VECTOR_LEDEND_VALUE,
            label=f"{VECTOR_LEDEND_VALUE} {VECTOR_LEGEND_UNIT}",
            labelpos="E",
            coordinates="axes",
            transform=ccrs.PlateCarree(),
        )

    def set_title(self, title_name: str) -> None:
        self.ax.set_title(title_name, fontsize=TITLE_SIZE)

    def save_figure(self, fig: Figure, save_dir: str, filename: str) -> None:
        os.makedirs(save_dir, exist_ok=True)
        out_path = os.path.join(save_dir, filename)
        fig.savefig(out_path, dpi=DPI)
