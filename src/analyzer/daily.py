from datetime import date
from typing import cast

import pandas as pd

from analyzer.base import AmedasDataAnalyzer
from analyzer.type import ObservedValuesContainer


class DailyDataAnalyzer(AmedasDataAnalyzer):
    def __init__(self, csv_filepath: str) -> None:
        super().__init__(csv_filepath)

    def get_observed_values(
        self, date: date, block_no: str, target_var: str
    ) -> ObservedValuesContainer:
        station = self.station_dict[block_no].station_name
        lon = self.station_dict[block_no].lon
        lat = self.station_dict[block_no].lat
        str_date = date.strftime("%Y-%m-%d")
        each_station_vars: pd.Series = cast(
            pd.Series, self.df.loc[str_date, block_no]
        )
        return ObservedValuesContainer(
            block_no=block_no,
            value=each_station_vars.at[station, target_var],
            lon=lon,
            lat=lat,
        )
