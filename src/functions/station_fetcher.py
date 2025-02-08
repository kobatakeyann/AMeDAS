import os

from config.scraping.output_path import STATIONS_CSV
from stations.csv_output import StationsDataProcessor


def fetch_stations_info(output_path: str = STATIONS_CSV) -> None:
    """Obtains information on observation points from the JMA page and saves it in a csv file.
    The observation point information is necessary for the scraping of observation values, so it is necessary to run the program once to obtain the information.
     Basically, only need to run it once, but to get the latest observation point information, run it again.

     Args:
         output_path (str, optional): path to save station csv file. Default is following to /src/config/output_path.py.
    """
    if os.path.exists(output_path):
        print(f"stations csv file already exists: {output_path}")
        return
    service = StationsDataProcessor()
    service.save_stations_info(output_path=output_path)
