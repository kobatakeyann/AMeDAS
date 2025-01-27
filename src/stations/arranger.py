import numpy as np
import pandas as pd


class StationsArranger:
    def __init__(
        self, affiliations_df: pd.DataFrame, detailed_json: dict
    ) -> None:
        self._affiliations_df = affiliations_df.copy()
        self._detailed_df = pd.DataFrame(detailed_json).transpose()

    def add_latlon_columns_for_keys(self) -> None:
        self._detailed_df["lat_degree"] = self._detailed_df["lat"].str[0]
        self._detailed_df["lat_minute"] = (
            self._detailed_df["lat"].str[1].astype(float)
        )
        self._detailed_df["lon_degree"] = self._detailed_df["lon"].str[0]
        self._detailed_df["lon_minute"] = (
            self._detailed_df["lon"].str[1].astype(float)
        )

    def convert_latlon_to_decimal(self) -> None:
        self._detailed_df["lat"] = (
            self._detailed_df["lat"].str[0]
            + self._detailed_df["lat"].str[1] / 60
        )
        self._detailed_df["lon"] = (
            self._detailed_df["lon"].str[0]
            + self._detailed_df["lon"].str[1] / 60
        )

    def add_observed_elements_columns(self) -> None:
        added_columns = [
            "temperture",
            "precipitation",
            "wind_direction",
            "wind",
            "sunshine",
            "snow_depth",
            "humidity",
            "pressure",
        ]
        observed_elements = np.array(
            self._detailed_df["elems"].apply(list).to_list()
        ).astype("int32")
        self._detailed_df[added_columns] = pd.DataFrame(
            observed_elements, index=self._detailed_df.index
        )
        self._detailed_df.drop(columns=["elems"], inplace=True)

    def merge_stations_info(self) -> pd.DataFrame:
        df_detailed = self._detailed_df.copy()
        df_affiliations = self._affiliations_df.copy().reset_index(drop=True)
        merged_df = df_affiliations.merge(
            df_detailed,
            left_on=[
                "station",
                "knName",
                "lat_degree",
                "lat_minute",
                "lon_degree",
                "lon_minute",
            ],
            right_on=[
                "kjName",
                "knName",
                "lat_degree",
                "lat_minute",
                "lon_degree",
                "lon_minute",
            ],
            how="left",
        )
        return merged_df.dropna().drop(
            columns=["lat_degree", "lat_minute", "lon_degree", "lon_minute"]
        )

    def save_stations_info_to_csv(
        self, df: pd.DataFrame, output_path: str
    ) -> None:
        df.to_csv(output_path, index=False, encoding="UTF-8")
