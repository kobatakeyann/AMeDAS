from typing import Literal

import pandas as pd
from pydantic import BaseModel

from util.path import generate_path


class StationInfoContainer(BaseModel, frozen=True):
    prec_no: str
    station_name: str
    block_no: str


class StationDataManager:
    def __init__(self) -> None:
        stations_csv_path = generate_path(
            "/data/stations_information/stations.csv"
        )
        self._df = pd.read_csv(stations_csv_path, dtype=str)

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def get_affiliation(self, block_no: str) -> StationInfoContainer:
        affiliation = self._df[self._df["block_no"] == block_no]
        return StationInfoContainer(
            prec_no=affiliation["prec_no"].item(),
            station_name=affiliation["enName"].item(),
            block_no=block_no,
        )

    def generate_station_url(
        self,
        prec_no: str,
        block_no: str,
        type: Literal["10min", "hourly", "daily"],
    ) -> str:
        BASE_URL = "http://www.data.jma.go.jp/obd/stats/etrn/view"
        if len(block_no) == 4:
            identifier = "a1"
        elif len(block_no) == 5:
            identifier = "s1"
        else:
            raise ValueError("Prec_no must be either 4 or 5 digits.")
        return f"{BASE_URL}/{type}_{identifier}.php?prec_no={prec_no}&block_no={block_no}"
