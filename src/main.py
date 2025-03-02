from datetime import date

from tools.composite import (
    visualize_composite_temperature,
    visualize_composite_wind,
)
from tools.observation_data_fetcher import fetch_observation_data
from tools.station_fetcher import fetch_stations_info
from tools.visualization import vizualize_temperature, vizualize_wind
from util.path import generate_path

saving_csv_filename = "sample.csv"
observation_data_csv_filepath = generate_path("/data/10min_data/sample.csv")
saving_composite_img_dir = generate_path("/img")
type = "hourly"
dates = [date(2022, 8, 8), date(2022, 8, 10)]
months = [date(2022, 8, 1), date(2022, 9, 1)]
prec_numbers = ["82", "83", "85", "86", "87"]


def main():
    fetch_stations_info()
    fetch_observation_data(
        prec_numbers=prec_numbers,
        type=type,
        dates=dates,
        months=None,
        csv_file_name=saving_csv_filename,
    )
    vizualize_wind(observed_data_path=observation_data_csv_filepath, type=type)
    # vizualize_temperature(
    #     observed_data_path=observation_data_csv_filepath, type=type
    # )


if __name__ == "__main__":
    main()
