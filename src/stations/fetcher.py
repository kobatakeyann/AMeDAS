import json

from api.data_fetcher import fetch_data


class StationsFetcher:
    JMA_STATIONS_PAGE_URL = (
        "https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture00.php"
    )
    STATIONS_DETAILS_URL = (
        "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"
    )

    @staticmethod
    def fetch_station_affiliation_html():
        return fetch_data(url=StationsFetcher.JMA_STATIONS_PAGE_URL)

    @staticmethod
    def fetch_stations_info() -> dict:
        response = fetch_data(StationsFetcher.STATIONS_DETAILS_URL)
        return json.loads(response)
