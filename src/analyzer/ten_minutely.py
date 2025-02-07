from datetime import datetime
from typing import cast

import pandas as pd
from pandas import DatetimeIndex

from analyzer.base import AmedasDataAnalyzer
from analyzer.type import ObservedValuesContainer


class TenminDataAnalyzer(AmedasDataAnalyzer):
    def __init__(self, csv_filepath: str) -> None:
        super().__init__(csv_filepath)

    def get_observed_values(
        self, datetime: datetime, block_no: str, target_var: str
    ) -> ObservedValuesContainer:
        station = self._station_dict[block_no].station_name
        lon = self._station_dict[block_no].lon
        lat = self._station_dict[block_no].lat
        str_datetime = datetime.strftime("%Y-%m-%d %H:%M:%S")
        each_station_vars: pd.Series = cast(
            pd.Series, self.df.loc[str_datetime, block_no]
        )
        return ObservedValuesContainer(
            block_no=block_no,
            value=each_station_vars.at[station, target_var],
            lon=lon,
            lat=lat,
        )

    def pivot_by_time_and_date(
        self, block_no: str, target_var: str
    ) -> pd.DataFrame:
        station = self._station_dict[block_no].station_name
        df = self.df[(block_no, station)].copy()
        assert isinstance(df.index, DatetimeIndex)
        df["date"] = df.index.date
        df["time"] = df.index.time
        return df.pivot(index="time", columns="date", values=target_var)
