from typing import Literal

from config.figure.gif import make_gif
from config.figure.output_path import FIGURE_IMAGE_DIR
from figure.drawing.temperature_plot import TemperaturePlot
from figure.drawing.wind_plot import WindPlot


def vizualize_temperature(
    observed_data_path: str,
    type: Literal[
        "10min",
        "hourly",
    ],
    save_root_dir: str = FIGURE_IMAGE_DIR,
    var_name: Literal[
        "temperature",
        "highest_temperature",
        "lowest_temperature",
        "mean_temperature",
    ] = "temperature",
):
    """The acquired temperature data for the entire period is plotted on a map and saved as an image.

    Args:
        observed_data_path (str): csv file path of the acquired observation data
        type (Literal[ &quot;10min&quot;, &quot;hourly&quot;, ]): Type of observation value to be obtained.
        save_root_dir (str, optional): root directory to save figure images. Default is following to src/config/figure/output_path.py.
        var_name (Literal[&quot;temperature&quot;], optional): variable name to plot. See csv column name. 'highest_temperature', 'lowest_temperature', 'mean_temperature' is available. Defaults to "temperature".
    """
    service = TemperaturePlot(csv_filepath=observed_data_path, type=type)
    service.make_all_figures(
        var_name=var_name,
        save_root_dir=save_root_dir,
        make_gif=make_gif,
    )


def vizualize_wind(
    observed_data_path: str,
    type: Literal[
        "10min",
        "hourly",
    ],
    save_root_dir: str = FIGURE_IMAGE_DIR,
):
    """The acquired wind data for the entire period is plotted on a map and saved as an image.

    Args:
        observed_data_path (str): csv file path of the acquired observation data
        type (Literal[ &quot;10min&quot;, &quot;hourly&quot;, ]): Type of observation value to be obtained.
        save_root_dir (str, optional): root directory to save figure images. Default is following to src/config/figure/output_path.py.
    """
    service = WindPlot(csv_filepath=observed_data_path, type=type)
    service.make_all_figures(save_root_dir=save_root_dir, make_gif=make_gif)
