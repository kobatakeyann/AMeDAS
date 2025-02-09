import pickle
from datetime import datetime, timedelta
from typing import Literal, NamedTuple, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cartopy.mpl.geoaxes import GeoAxes

from analyzer.hourly import HourlyDataAnalyzer
from analyzer.ten_minutely import TenMinuteDataAnalyzer
from config.figure.base_map import LAT_BOTTOM, LAT_TOP, LON_LEFT, LON_RIGHT
from config.figure.figure import TITLE_NAME
from config.figure.gif import GIF_INTERVAL_TIME
from figure.drawing.factory import FigureFactory
from figure.drawing.helper.color import get_color_from_value
from figure.drawing.methods import PlotMethods
from gif.gif import make_gif_from_imgs
from util.date_formatter import PaddedDate, PaddedDatetime


class ValuesWithCoords(NamedTuple):
    lon: list[float]
    lat: list[float]
    value: list[float]


class TemperaturePlot(FigureFactory):
    _type: Literal["10min", "hourly"]

    def __init__(
        self, csv_filepath: str, type: Literal["10min", "hourly"]
    ) -> None:
        super().__init__()
        if type == "10min":
            self._analyzer = TenMinuteDataAnalyzer(csv_filepath)
        elif type == "hourly":
            self._analyzer = HourlyDataAnalyzer(csv_filepath)
        else:
            raise ValueError(
                "Invalid type. Please input type from '10min', 'hourly'."
            )
        self._type = type

    def _get_coords_and_values(
        self, jst_time: datetime, var_name: str
    ) -> ValuesWithCoords:
        lons, lats, values = [], [], []
        for block_no in self._analyzer.block_numbers:
            observed_values = self._analyzer.get_observed_values(
                jst_time, block_no, var_name
            )
            lons.append(observed_values.lon)
            lats.append(observed_values.lat)
            values.append(observed_values.value)
        return ValuesWithCoords(lon=lons, lat=lats, value=values)

    def _get_title(self, jst_time: datetime) -> str:
        padded_dt = PaddedDatetime(jst_time)
        base_title = f"{self._type} {TITLE_NAME}"
        match self._type:
            case "10min":
                return f"{base_title} {padded_dt.year}/{padded_dt.month}/{padded_dt.day} {padded_dt.hour}{padded_dt.minute}JST"
            case "hourly":
                hour_before = (jst_time - timedelta(hours=1)).hour
                return f"{base_title} {padded_dt.year}/{padded_dt.month}/{padded_dt.day} {str(hour_before).zfill(2)}00-{padded_dt.hour}00JST"
            case "daily":
                return f"{base_title} {padded_dt.year}/{padded_dt.month}/{padded_dt.day}"

    def make_figure(
        self, jst_time: datetime, var_name: str, save_dir: str
    ) -> None:
        basefig = pickle.loads(self._basefig)
        ax = cast(GeoAxes, basefig.get_axes()[0])
        target_ax = PlotMethods(ax)
        value_with_coords = self._get_coords_and_values(jst_time, var_name)
        for lon, lat, value in zip(
            value_with_coords.lon,
            value_with_coords.lat,
            value_with_coords.value,
        ):
            if (
                not np.isnan(value)
                and LAT_BOTTOM <= lat <= LAT_TOP
                and LON_LEFT <= lon <= LON_RIGHT
            ):
                color = get_color_from_value(value)
                space = 0.03
                target_ax.plot_text_label(lon, lat + space, str(value), color)
                target_ax.ax.plot(
                    lon, lat, marker=".", color="navy", markersize=3
                )
        target_ax.set_title(title_name=self._get_title(jst_time))
        padded_dt = PaddedDatetime(jst_time)
        filename = f"{padded_dt.year}{padded_dt.month}{padded_dt.day}{padded_dt.hour}{padded_dt.minute}.jpg"
        target_ax.save_figure(
            fig=basefig,
            save_dir=save_dir,
            filename=filename,
        )
        plt.cla()
        plt.close()

    def make_all_figures(
        self, var_name: str, save_root_dir: str, make_gif: bool
    ) -> None:
        for datetime in self._analyzer.get_datetimes():
            print(f"Now making {datetime} figure…")
            if not (datetime.hour == 0 and datetime.minute == 0):
                padded_date = PaddedDate(datetime.date())
                each_save_dir = f"{save_root_dir}/{self._type}/{padded_date.year}/{padded_date.month}/{padded_date.day}"
                self.make_figure(datetime, var_name, each_save_dir)
            elif make_gif:
                self.make_figure(datetime, var_name, each_save_dir)
                make_gif_from_imgs(
                    img_dir_path=each_save_dir,
                    saved_gif_path=f"{each_save_dir}/temperature.gif",
                    interval_time=GIF_INTERVAL_TIME,
                )
                print("Successfully made gif!")

    def _get_average_temperature_df(self, var_name: str) -> pd.DataFrame:
        temperature_ave_df = pd.DataFrame()
        for block_no in self._analyzer.block_numbers:
            temperature_df = self._analyzer.pivot_by_time_and_date(
                block_no, var_name
            )
            temperature_ave = temperature_df.mean(axis=1)
            temperature_ave = self._analyzer.sort_index_in_correct_order(
                temperature_ave
            )
            temperature_ave_df[block_no] = temperature_ave
        return temperature_ave_df

    def make_composite_temperature(
        self, var_name: str, save_dir: str, make_gif: bool
    ) -> None:
        temperature_ave_df = self._get_average_temperature_df(var_name)
        lons = [
            self._analyzer.station_dict[block_no].lon
            for block_no in self._analyzer.block_numbers
        ]
        lats = [
            self._analyzer.station_dict[block_no].lat
            for block_no in self._analyzer.block_numbers
        ]
        for temp_series in temperature_ave_df.iterrows():
            exe_time, temp_rows = temp_series
            print(f"Now making {exe_time} figure…")
            basefig = pickle.loads(self._basefig)
            ax = cast(GeoAxes, basefig.get_axes()[0])
            target_ax = PlotMethods(ax)
            for lon, lat, value in zip(lons, lats, temp_rows.values):
                if (
                    not np.isnan(value)
                    and LAT_BOTTOM <= lat <= LAT_TOP
                    and LON_LEFT <= lon <= LON_RIGHT
                ):
                    value = round(value, 1)
                    color = get_color_from_value(value)
                    space = 0.03
                    target_ax.plot_text_label(
                        lon, lat + space, str(value), color
                    )
                    target_ax.ax.plot(
                        lon, lat, marker=".", color="navy", markersize=3
                    )
            if exe_time == "00:00:00":
                exe_time = "24:00:00"
            filename = f"{str(exe_time).replace(":","")[:4]}jst.jpg"
            if self._type == "10min":
                title = f"composite {TITLE_NAME} {str(exe_time).replace(":","")[:4]}JST"
            elif self._type == "hourly":
                hour = str(exe_time).split(":")[0]
                hour_before = str(int(hour) - 1).zfill(2)
                title = f"composite {TITLE_NAME} {hour_before}00-{hour}00JST"
            target_ax.set_title(title_name=title)
            target_ax.save_figure(
                fig=basefig,
                save_dir=f"{save_dir}/composite/temperature",
                filename=filename,
            )
            plt.cla()
            plt.close()
        if make_gif:
            make_gif_from_imgs(
                img_dir_path=f"{save_dir}/composite/temperature",
                saved_gif_path=f"{save_dir}/composite.gif",
                interval_time=GIF_INTERVAL_TIME,
            )
            print("Successfully made gif!")
