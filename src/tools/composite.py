from typing import Literal

from config.figure.gif import make_gif
from figure.drawing.temperature_plot import TemperaturePlot
from figure.drawing.wind_plot import WindPlot


def visualize_composite_temperature(
    observed_data_path: str,
    type: Literal[
        "10min",
        "hourly",
    ],
    save_dir: str,
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
        type (Literal[ "10min", "hourly", ]): Type of observation value to be obtained.
        save_dir (str, optional): directory to save figure images.
        var_name (Literal["temperature"], optional): variable name to plot. See csv column name. 'highest_temperature', 'lowest_temperature', 'mean_temperature' is available. Defaults to "temperature".
    """
    service = TemperaturePlot(csv_filepath=observed_data_path, type=type)
    service.make_composite_temperature(
        var_name=var_name,
        save_dir=save_dir,
        make_gif=make_gif,
    )


def visualize_composite_wind(
    observed_data_path: str,
    type: Literal[
        "10min",
        "hourly",
    ],
    save_dir: str,
):
    """The acquired wind data for the entire period is plotted on a map and saved as an image.

    Args:
        observed_data_path (str): csv file path of the acquired observation data
        type (Literal[ "10min", "hourly", ]): Type of observation value to be obtained.
        save_dir (str, optional): directory to save figure images.
    """
    service = WindPlot(csv_filepath=observed_data_path, type=type)
    service.make_composite_wind_figure(save_dir=save_dir, make_gif=make_gif)
