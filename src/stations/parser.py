import re
from typing import NamedTuple

import pandas as pd
from bs4 import BeautifulSoup

from api.data_fetcher import fetch_data
from api.url_parser import get_query_params


class AreaInfoContainer(NamedTuple):
    area_name: list[str]
    prec_no: list[str]


class StationsParser:
    def __init__(self, area_html: bytes) -> None:
        self._area_html = BeautifulSoup(area_html, features="html.parser")

    def get_area_affiliations(self) -> AreaInfoContainer:
        elements = self._area_html.find_all("area")
        area_names, prec_no_list = [], []
        for element in elements:
            area_name = element["alt"]
            prec_no = get_query_params(element["href"])["prec_no"][0]
            area_names.append(area_name)
            prec_no_list.append(prec_no)
        return AreaInfoContainer(area_names, prec_no_list)

    def parse_area_html(
        self, html: bytes, area_name: str, prec_no: str
    ) -> list[dict]:
        soup = BeautifulSoup(html, features="html.parser")
        elements = soup.find_all("area")
        st_info = []
        for element in elements:
            if "onmouseover" in element.attrs:
                target_attr = element["onmouseover"]
                match = re.search(r"viewPoint\((.*?)\)", target_attr)
                if match:
                    items = [
                        item.strip("'") for item in match.group(1).split(",")
                    ]
                    st_info.append(
                        {
                            "area": area_name,
                            "station": element["alt"],
                            "knName": items[3],
                            "prec_no": prec_no,
                            "block_no": items[1],
                            "lat_degree": int(items[4]),
                            "lat_minute": float(items[5]),
                            "lon_degree": int(items[6]),
                            "lon_minute": float(items[7]),
                        }
                    )
                else:
                    raise ValueError(
                        "No match found. Target information is missing."
                    )
        return st_info

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
            parsed_results = self.parse_area_html(html, area_name, prec_no)
            stations_info.extend(parsed_results)
        return pd.DataFrame(stations_info).drop_duplicates()
