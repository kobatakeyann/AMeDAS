from stations.arranger import StationsArranger
from stations.fetcher import StationsFetcher
from stations.parser import StationsParser


class StationsDataProcessor:
    def __init__(self) -> None:
        self._affiliations_html = (
            StationsFetcher.fetch_station_affiliation_html()
        )
        self._detailed_json = StationsFetcher.fetch_stations_json()

    def save_stations_info(
        self,
        output_path: str,
        include_inactive_stations: bool = False,
    ) -> None:
        """Fetch, process, merge, and save AMeDAS stations information to a csv file.

        Args:
            output_path (str): Path to save the information as a csv file.
            include_inactive_stations (bool) : If True, include currently inactive stations in the output.
        """
        # Parse the affiliation html.
        parser = StationsParser(self._affiliations_html)
        affiliation_info = parser.get_area_affiliations()
        affiliated_df = parser.get_stations_info(affiliation_info)

        # Arrange the detailed information.
        arranger = StationsArranger(affiliated_df, self._detailed_json)
        arranger.add_latlon_columns_for_keys()
        arranger.convert_latlon_to_decimal()
        arranger.add_observed_elements_columns()

        # Merge with the affiliation information.
        merged_df = arranger.merge_stations_info(
            include_inactive_stations=include_inactive_stations
        )
        arranger.save_stations_info_to_csv(
            df=merged_df, output_path=output_path
        )
