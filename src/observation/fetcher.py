import os
from calendar import monthrange
from datetime import date, datetime
from time import sleep
from typing import Literal

import pandas as pd

from observation.arranger import ObservedDataArranger
from observation.station import StationDataManager
from util.path import generate_path
from util.time import DateArranger


class ObservedDataFetcher:
    _type: Literal["10min", "hourly", "daily"]

    def __init__(
        self,
        block_numbers: list[str],
        type: Literal["10min", "hourly", "daily"],
        dates: list[date] | None = None,
        months: list[date] | None = None,
    ) -> None:

        self._block_numbers = block_numbers
        self._dates = dates
        self._months = months
        self._type = type
        self._validate_input()

    def _validate_input(self):
        if (not self._block_numbers) or (not self._dates):
            raise ValueError(
                "Stations' block numbers and datetimes must be provided at least one."
            )
        if (self._dates is None) and (self._months is None):
            raise ValueError("Either dates or months must be provided.")

    def get_target_urls(self) -> list[str]:
        urls = []
        self._station_names = []
        station_manager = StationDataManager()
        for blocK_no in self._block_numbers:
            affiliation = station_manager.get_affiliation(blocK_no)
            target_url = station_manager.generate_station_url(
                affiliation.prec_no, affiliation.block_no, self._type
            )
            urls.append(target_url)
            self._station_names.append(affiliation.station_name)
        return urls

    def create_base_dataframe(self, target_date: date) -> pd.DataFrame:
        match self._type:
            case "10min":
                data_num = 144
                interval = "10min"
                start = datetime(
                    target_date.year, target_date.month, target_date.day, 0, 10
                )
            case "hourly":
                data_num = 24
                interval = "h"
                start = datetime(
                    target_date.year, target_date.month, target_date.day, 1, 0
                )
            case "daily":
                data_num = monthrange(target_date.year, target_date.month)[1]
                interval = "D"
                start = date(target_date.year, target_date.month, 1)
        df = pd.DataFrame(
            pd.date_range(start=start, periods=data_num, freq=interval),
            columns=["datetime"],
        )
        return df

    def fetch_observed_values(self, urls: list[str]) -> pd.DataFrame:
        each_date_df = []
        if self._dates is not None:
            dates = self._dates
        if (self._months is not None) and (self._type == "daily"):
            dates = self._months
        for date in dates:
            base_df = self.create_base_dataframe(date)
            year, month, day = DateArranger(date).get_padded_date()
            match self._type:
                case "10min":
                    query_params = (
                        f"year={year}&month={month}&day={day}&view=p1"
                    )
                case "hourly":
                    query_params = f"year={year}&month={month}&day={day}&view="
                case "daily":
                    query_params = f"year={year}&month={month}&day=&view="
            each_station_df = []
            for station_name, base_url in zip(self._station_names, urls):
                url = f"{base_url}&{query_params}"
                processor = ObservedDataArranger(page_url=url, type=self._type)
                processor.add_lacking_columns()
                processor.add_station_name_to_columns(station_name)
                each_station_df.append(processor.df)
                sleep(0.05)
            df = pd.concat([base_df] + each_station_df, axis=1)
            each_date_df.append(df)
        return pd.concat(each_date_df, axis=0).reset_index(drop=True)

    def arrange_fetched_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = ObservedDataArranger.replace_missing_data(df)
        df = ObservedDataArranger.replace_wind_direction(df)
        return df

    def save_as_csv(self, df: pd.DataFrame, file_name: str) -> None:
        saving_dir = generate_path(f"/data/{self._type}_data")
        os.makedirs(saving_dir, exist_ok=True)
        csv_path = os.path.join(saving_dir, file_name)
        df.to_csv(
            csv_path,
            header=True,
            index=False,
            na_rep="nan",
        )
