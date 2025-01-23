from stations.arranger import AmedasStationsArranger
from stations.data_processor import AmedasStationsArranger
from stations.fetcher import AmedasStationsFetcher
from stations.parser import AmedasStationsParser


class AmedasStationsDataProcessor:
    def __init__(self) -> None:
        self._fetcher = AmedasStationsFetcher()

    def save_stations_info(self, output_path) -> None:
        staions_html = self._fetcher.fetch_station_page_html()
        self._parser = AmedasStationsParser(staions_html)
        area_info = self._parser.extract_areas()
        stations_info = self._parser.get_stations_info(area_info)
        self._arranger = AmedasStationsArranger(stations_info)
        self._arranger.clean_stations_info()
        self._arranger.save_stations_info_to_csv(output_path)
