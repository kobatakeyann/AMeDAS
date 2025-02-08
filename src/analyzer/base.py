from typing import NamedTuple

import numpy as np
import pandas as pd
from pydantic import BaseModel

from config.scraping.output_path import STATIONS_CSV
from constants.missing_value import MISSING_VALUE
from util.path import generate_path


class Location(NamedTuple):
    lon: float
    lat: float


class StationInfo(BaseModel, frozen=True):
    station_name: str
    lon: float
    lat: float


class AmedasDataAnalyzer:
    def __init__(self, csv_filepath: str) -> None:
        self._stations_df = pd.read_csv(STATIONS_CSV, dtype=str)

        self.df = pd.read_csv(csv_filepath, header=[0, 1, 2], index_col=0)
        self.df.columns.names = ["block_no", "station", "element"]
        self.df.index = pd.to_datetime(self.df.index)
        self._missing_value_to_nan()
        self._set_stations_dict_attr()

    @property
    def block_numbers(self) -> list[str]:
        BLOCK_NO_COLUMN_LEVEL = 0
        return (
            self.df.columns.get_level_values(BLOCK_NO_COLUMN_LEVEL)
            .unique()
            .to_list()
        )

    @property
    def station_names(self) -> list[str]:
        STATION_COLUMN_LEVEL = 1
        level_0_columns = self.df.columns.get_level_values(
            STATION_COLUMN_LEVEL
        )
        station_names = list(set(level_0_columns))
        return station_names

    def _set_stations_dict_attr(self) -> None:
        station_dict: dict[str, StationInfo] = {}
        for multi_col in self.df.columns:
            block_no, station, _ = multi_col
            location = self.get_lonlat(block_no)
            station_dict[block_no] = StationInfo(
                station_name=station,
                lon=location.lon,
                lat=location.lat,
            )
        self.station_dict = station_dict

    def get_lonlat(self, block_no: str) -> Location:
        match_row = self._stations_df[
            self._stations_df["block_no"] == block_no
        ]
        if match_row.empty:
            raise ValueError(f"block_number {block_no} is not found.")
        lon = match_row["lon"].values[0]
        lat = match_row["lat"].values[0]
        return Location(lon=lon, lat=lat)

    def get_datetimes(self) -> list[pd.Timestamp]:
        return self.df.index.to_list()

    def _missing_value_to_nan(self) -> None:
        self.df = self.df.replace(float(MISSING_VALUE), np.nan)
