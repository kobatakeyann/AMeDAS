from typing import NamedTuple

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from api.data_fetcher import fetch_data
from api.url_parser import get_query_params


class AreaInfoContainer(NamedTuple):
    area_name: list[str]
    prec_no: list[str]


class AmedasStationsParser:
    def __init__(self, html: BeautifulSoup) -> None:
        self._html = html

    def extract_areas(self) -> AreaInfoContainer:
        elements = self._html.find_all("area")
        area_names, prec_no_list = [], []
        for element in elements:
            area_name = element["alt"]
            prec_no = get_query_params(element["href"])["prec_no"][0]
            area_names.append(area_name)
            prec_no_list.append(prec_no)
        return AreaInfoContainer(area_names, prec_no_list)

    def get_stations_info(self, area_info: AreaInfoContainer) -> pd.DataFrame:
        BASE_URL = "https://www.data.jma.go.jp/obd/stats/etrn/select/"
        stations_info = []
        area_names = area_info.area_name
        prec_no_list = area_info.prec_no
        for area_name, prec_no in zip(area_names, prec_no_list):
            url = (
                BASE_URL
                + f"prefecture.php?prec_no={prec_no}&block_no=&year=&month=&day=&view="
            )
            html = fetch_data(url)
            soup = BeautifulSoup(html, features="html.parser")
            elements = soup.find_all("area")
            for element in elements:
                station_name = element["alt"]
                block_no = get_query_params(element["href"]).get(
                    "block_no", [np.nan]
                )[0]
                stations_info.append(
                    {
                        "station": station_name,
                        "area": area_name,
                        "prec_no": prec_no,
                        "block_no": block_no,
                    }
                )
        return pd.DataFrame(stations_info)
