import pandas as pd


class AmedasStationsArranger:
    def __init__(self, stations_df: pd.DataFrame) -> None:
        self._stations_df = stations_df.copy()

    def clean_stations_info(self) -> None:
        self._stations_df = self._stations_df.drop_duplicates().dropna()

    def save_stations_info_to_csv(self, output_path: str) -> None:
        self._stations_df.to_csv(output_path, index=False, encoding="UTF-8")
