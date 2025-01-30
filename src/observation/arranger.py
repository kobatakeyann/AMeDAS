from typing import Literal

import numpy as np
import pandas as pd

from observation.constants import (
    COLUMNS_10MIN,
    COLUMNS_DAILY,
    COLUMNS_HOURLY,
    MISSING_VALUE,
    WIND_DIRECTION,
)


class ObservedDataArranger:
    def __init__(
        self, page_url: str, type: Literal["10min", "hourly", "daily"]
    ) -> None:
        self._type = type
        self._df = pd.read_html(page_url)[0].reset_index(drop=True)
        self._drop_time_column()

    def _drop_time_column(self) -> None:
        self._df = self._df.iloc[:, 1:]

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def add_lacking_columns(self) -> None:
        match self._type:
            case "10min":
                if "現地" not in self._df.columns.get_level_values(-1):
                    self._df.insert(0, "現地", np.nan)
                    self._df.insert(1, "海面", np.nan)
                    return
            case "hourly":
                if "現地" not in self._df.columns.get_level_values(1):
                    self._df.insert(0, "現地", np.nan)
                    self._df.insert(1, "海面", np.nan)
                    self._df.insert(10, "全天日射量", np.nan)
                    self._df.insert(13, "雲量", np.nan)
                    self._df.insert(14, "視程", np.nan)
                else:
                    self._df.drop(columns="天気", level=1, inplace=True)
                return
            case "daily":
                if "現地" not in self._df.columns.get_level_values(1):
                    self._df.insert(0, "現地平均", np.nan)
                    self._df.insert(1, "海面平均", np.nan)
                    self._df.insert(19, "天気概況(昼)", np.nan)
                    self._df.insert(20, "天気概況(夜)", np.nan)
                else:
                    self._df.insert(15, "最多風向", np.nan)
                return

    def add_id_to_columns(self, station_name: str, block_no: str) -> None:
        match self._type:
            case "10min":
                elements = COLUMNS_10MIN
            case "hourly":
                elements = COLUMNS_HOURLY
            case "daily":
                elements = COLUMNS_DAILY
        multi_index = pd.MultiIndex.from_tuples(
            tuples=[(block_no, station_name, elem) for elem in elements],
            names=["block_no", "station", "element"],
        )
        self._df.columns = multi_index

    @staticmethod
    def replace_missing_data(df: pd.DataFrame) -> pd.DataFrame:
        df = df.replace(
            {
                "///": MISSING_VALUE,
                "×": MISSING_VALUE,
                "#": MISSING_VALUE,
                "--": MISSING_VALUE,
            },
            regex=False,
        )
        df = df.replace(
            {
                r".*\)": MISSING_VALUE,
                r".*\s\]": MISSING_VALUE,
            },
            regex=True,
        )
        return df

    @staticmethod
    def replace_wind_direction(df: pd.DataFrame) -> pd.DataFrame:
        df = df.replace(WIND_DIRECTION)
        return df
