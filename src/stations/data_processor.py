from stations.arranger import AmedasStationsArranger
from stations.data_processor import AmedasStationsArranger
from stations.fetcher import AmedasStationsFetcher
from stations.parser import AmedasStationsParser


class AmedasStationsDataProcessor:
    def __init__(self) -> None:
        self._affiliations_html = (
            AmedasStationsFetcher.fetch_station_affiliation_html()
        )
        self._detailed_json = AmedasStationsFetcher.fetch_stations_info()

    def save_stations_info(self, output_path: str) -> None:
        """Fetch, process, merge, and save AMeDAS stations information to a csv file.

        Args:
            output_path (str): Path to save the information as a csv file.
        """
        # Parse the affiliation html.
        parser = AmedasStationsParser(self._affiliations_html)
        affiliation_info = parser.get_area_affiliations()
        affiliated_df = parser.attach_block_number(affiliation_info)

        # Arrange the detailed information.
        arranger = AmedasStationsArranger(affiliated_df, self._detailed_json)
        arranger.convert_latlon_to_decimal()
        arranger.add_observed_elements_columns()

        # Merge with the affiliation information.
        merged_df = arranger.merge_stations_info()
        arranger.save_stations_info_to_csv(
            df=merged_df, output_path=output_path
        )
