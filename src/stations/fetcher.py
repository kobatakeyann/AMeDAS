import json

from api.data_fetcher import fetch_data


class AmedasStationsFetcher:
    JMA_STATION_PAGE_URL = "https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture00.php?prec_no=&block_no=&year=&month=&day=&view="
    STATION_INFO_URL = (
        "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"
    )

    @staticmethod
    def fetch_station_affiliation_html():
        return fetch_data(url=AmedasStationsFetcher.JMA_STATION_PAGE_URL)

    @staticmethod
    def fetch_stations_info() -> dict:
        response = fetch_data(AmedasStationsFetcher.STATION_INFO_URL)
        return json.loads(response)
