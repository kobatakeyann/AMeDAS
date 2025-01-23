from stations.arranger import AmedasStationsArranger
from stations.data_processor import AmedasStationsArranger
from stations.fetcher import AmedasStationsFetcher
from stations.parser import AmedasStationsParser


class AmedasStationsDataProcessor:
    def __init__(self) -> None:
        self._stations_html = AmedasStationsFetcher.fetch_station_page_html()

    def save_stations_info(self, output_path: str) -> None:
        """Fetch, process, and save AMeDAS stations information to a csv file.

        Args:
            output_path (str): Path to save the information as a csv file.
        """
        parser = AmedasStationsParser(self._stations_html)
        area_info = parser.extract_areas()
        stations_info = parser.get_stations_info(area_info)
        arranger = AmedasStationsArranger(stations_info)
        arranger.clean_stations_info()
        arranger.save_stations_info_to_csv(output_path)
