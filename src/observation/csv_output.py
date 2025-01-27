from datetime import date
from typing import Literal

from observation.fetcher import ObservedDataFetcher
from observation.station import StationDataManager


class ObservedDataProcessor:
    _type: Literal["10min", "hourly", "daily"]

    def __init__(
        self,
        prec_numbers: list[str],
        type: Literal["10min", "hourly", "daily"],
        dates: list[date] | None = None,
        months: list[date] | None = None,
    ) -> None:
        self._prec_numbers = prec_numbers
        self._dates = dates
        self._months = months
        self._type = type

    def get_block_numbers(self, prec_numbers: list[str]) -> list[str]:
        stations_df = StationDataManager().df
        block_numbers = stations_df[stations_df["prec_no"].isin(prec_numbers)][
            "block_no"
        ]
        return block_numbers.to_list()

    def save_observed_data(self, csv_file_name: str) -> None:
        fetcher = ObservedDataFetcher(
            block_numbers=self.get_block_numbers(self._prec_numbers),
            type=self._type,
            dates=self._dates,
            months=self._months,
        )
        target_urls = fetcher.get_target_urls()
        fetched_df = fetcher.fetch_observed_values(target_urls)
        arranged_df = fetcher.arrange_fetched_df(fetched_df)
        fetcher.save_as_csv(df=arranged_df, file_name=csv_file_name)
