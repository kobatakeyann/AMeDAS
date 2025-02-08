import pickle
from datetime import datetime, timedelta
from typing import Literal, NamedTuple, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cartopy.mpl.geoaxes import GeoAxes

from analyzer.helper.wind import get_wind_components
from analyzer.hourly import HourlyDataAnalyzer
from analyzer.ten_minutely import TenMinuteDataAnalyzer
from config.figure.figure import TITLE_NAME
from config.figure.gif import GIF_INTERVAL_TIME
from figure.drawing.factory import FigureFactory
from figure.drawing.methods import PlotMethods
from gif.gif import make_gif_from_imgs
from util.date_formatter import PaddedDate, PaddedDatetime


class ValuesWithCoords(NamedTuple):
    lon: list[float]
    lat: list[float]
    u: list[float]
    v: list[float]


class WindPlot(FigureFactory):
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
                "Invalid type. Please input type from '10min', 'hourly', 'daily'."
            )
        self._type = type

    def get_coords_and_values(self, jst_time: datetime) -> ValuesWithCoords:
        lons, lats, u_components, v_components = [], [], [], []
        for block_no in self._analyzer.block_numbers:
            wind_speed = self._analyzer.get_observed_values(
                jst_time, block_no, "mean_ws"
            )
            wind_direction = self._analyzer.get_observed_values(
                jst_time, block_no, "mean_wd"
            )
            u, v = get_wind_components(wind_speed.value, wind_direction.value)
            lons.append(wind_direction.lon)
            lats.append(wind_direction.lat)
            u_components.append(u)
            v_components.append(v)
        return ValuesWithCoords(
            lon=lons, lat=lats, u=u_components, v=v_components
        )

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

    def make_figure(self, jst_time: datetime, save_dir: str) -> None:
        basefig = pickle.loads(self._basefig)
        ax = cast(GeoAxes, basefig.get_axes()[0])
        target_ax = PlotMethods(ax)
        value_with_coords = self.get_coords_and_values(jst_time)
        target_ax.plot_vector(
            value_with_coords.lon,
            value_with_coords.lat,
            value_with_coords.u,
            value_with_coords.v,
        )
        target_ax.plot_legend_vector()
        padded_dt = PaddedDatetime(jst_time)
        target_ax.set_title(title_name=self._get_title(jst_time))
        filename = f"{padded_dt.year}{padded_dt.month}{padded_dt.day}{padded_dt.hour}{padded_dt.minute}.jpg"
        target_ax.save_figure(
            fig=basefig,
            save_dir=save_dir,
            filename=filename,
        )
        plt.cla()
        plt.close()

    def make_all_figures(self, save_root_dir: str, make_gif: bool) -> None:
        for datetime in self._analyzer.get_datetimes():
            print(f"Now making {datetime} figure…")
            if not (datetime.hour == 0 and datetime.minute == 0):
                padded_date = PaddedDate(datetime.date())
                each_save_dir = f"{save_root_dir}/{self._type}/{padded_date.year}/{padded_date.month}/{padded_date.day}"
                self.make_figure(datetime, each_save_dir)
            elif make_gif:
                self.make_figure(datetime, each_save_dir)
                make_gif_from_imgs(
                    img_dir_path=each_save_dir,
                    saved_gif_path=f"{each_save_dir}/wind.gif",
                    interval_time=GIF_INTERVAL_TIME,
                )
                print("Successfully made gif!")

    def _get_averge_wind_uv_df(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        u_ave_df, v_ave_df = pd.DataFrame(), pd.DataFrame()
        for block_no in self._analyzer.block_numbers:
            wind_speed = self._analyzer.pivot_by_time_and_date(
                block_no, "mean_ws"
            )
            wind_direction = self._analyzer.pivot_by_time_and_date(
                block_no, "mean_wd"
            )
            wind_speed.replace(-888.8, 0, inplace=True)
            wind_u = wind_speed * (-np.sin(np.radians(wind_direction)))
            wind_v = wind_speed * (-np.cos(np.radians(wind_direction)))
            u_ave, v_ave = wind_u.mean(axis=1), wind_v.mean(axis=1)
            u_ave = self._analyzer.sort_index_in_correct_order(u_ave)
            v_ave = self._analyzer.sort_index_in_correct_order(v_ave)
            u_ave_df[block_no], v_ave_df[block_no] = u_ave, v_ave
        return u_ave_df, v_ave_df

    def make_composite_wind_figure(
        self, save_dir: str, make_gif: bool
    ) -> None:
        u_ave_df, v_ave_df = self._get_averge_wind_uv_df()
        lons = [
            self._analyzer.station_dict[block_no].lon
            for block_no in self._analyzer.block_numbers
        ]
        lats = [
            self._analyzer.station_dict[block_no].lat
            for block_no in self._analyzer.block_numbers
        ]
        for u_series, v_series in zip(
            u_ave_df.iterrows(), v_ave_df.iterrows()
        ):
            exe_time, u_rows = u_series
            _, v_rows = v_series
            print(f"Now making {exe_time} figure…")
            basefig = pickle.loads(self._basefig)
            ax = cast(GeoAxes, basefig.get_axes()[0])
            u_values = cast(list[float], list(u_rows.values))
            v_values = cast(list[float], list(v_rows.values))
            target_ax = PlotMethods(ax)
            target_ax.plot_vector(
                lons,
                lats,
                u_values,
                v_values,
            )
            target_ax.plot_legend_vector()
            if exe_time == "00:00:00":
                exe_time = "24:00:00"
            filename = f"{str(exe_time).replace(":","")[:4]}jst.jpg"
            if self._type == "10min":
                title = f"composite {TITLE_NAME} mean wind {str(exe_time).replace(":","")[:4]}JST"
            elif self._type == "hourly":
                hour = str(exe_time).split(":")[0]
                hour_before = str(int(hour) - 1).zfill(2)
                title = f"composite {TITLE_NAME} mean wind {hour_before}00-{hour}00JST"
            target_ax.set_title(title_name=title)
            target_ax.save_figure(
                fig=basefig, save_dir=save_dir, filename=filename
            )
            plt.cla()
            plt.close()
        if make_gif:
            make_gif_from_imgs(
                img_dir_path=save_dir,
                saved_gif_path=f"{save_dir}/composite.gif",
                interval_time=GIF_INTERVAL_TIME,
            )
            print("Successfully made gif!")
