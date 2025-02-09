from datetime import datetime
from typing import cast
from warnings import filterwarnings

import pandas as pd
from pandas import DatetimeIndex

from analyzer.base import AmedasDataAnalyzer
from analyzer.type import ObservedValuesContainer


class HourlyDataAnalyzer(AmedasDataAnalyzer):
    filterwarnings("ignore")

    def __init__(self, csv_filepath: str) -> None:
        super().__init__(csv_filepath)

    def get_observed_values(
        self, datetime: datetime, block_no: str, target_var: str
    ) -> ObservedValuesContainer:
        station = self.station_dict[block_no].station_name
        lon = self.station_dict[block_no].lon
        lat = self.station_dict[block_no].lat
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
        station = self.station_dict[block_no].station_name
        df = self.df[(block_no, station)].copy()
        assert isinstance(df.index, DatetimeIndex)
        df["date"] = df.index.date
        df["time"] = df.index.time
        return df.pivot(index="time", columns="date", values=target_var)

    def get_average_by_time(self, block_no: str, target_var: str) -> pd.Series:
        pivotted_df = self.pivot_by_time_and_date(block_no, target_var)
        df = pivotted_df.mean(axis=1)
        return df._sort_index_in_correct_order()

    def get_std_by_time(self, block_no: str, target_var: str) -> pd.Series:
        pivotted_df = self.pivot_by_time_and_date(block_no, target_var)
        df = pivotted_df.std(axis=1)
        return self.sort_index_in_correct_order(df)

    def sort_index_in_correct_order(self, df: pd.Series) -> pd.Series:
        df = pd.concat([df.iloc[1:], pd.Series(df.iloc[0])])
        df.index = pd.date_range(
            start="01:00:00", freq="h", periods=24
        ).strftime("%H:%M:%S")
        return df
