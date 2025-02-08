from datetime import date
from typing import Literal

from observation.csv_output import ObservedDataProcessor


def fetch_observation_data(
    prec_numbers: list[str],
    type: Literal["10min", "hourly", "daily"],
    dates: list[date] | None,
    months: list[date] | None,
    csv_file_name: str,
) -> None:
    """Scraping observation data from the JMA AMeDAS page and saving it to a csv file.
    Available AMeDAS observation data is three types: 10-minute data, hourly data, and daily data.
    Specify the prec_number corresponding to the prefecture you wish to obtain (see /src/constants/prec_number.py),
    Specify the type of data you want to retrieve (type) and the dates you want to retrieve (dates).
    If you want to get data for multiple days, please add them to the list.If you want to specify a daily value, specify any day of the month.
    Args:
        prec_numbers (list[str]): List of prec numbers for the prefecture you wish to retrieve.
        type (Literal[&quot;10min&quot;, &quot;hourly&quot;, &quot;daily&quot;]): Type of observation value to be obtained.
        dates (list[date] | None): List of dates retrieved for 10-minute data and hourly data
        months (list[date] | None): List of dates retrieved for daily data
        csv_file_name (str): csv filename to save the observation data.
    Examples:
        fetch_observation_data(
        prec_numbers=["82", "83", "85", "86", "87"],
        type="hourly",
        dates=[date(2022, 8, 8), date(2022, 8, 10)],
        months=None,
        csv_file_name="sample_hourly.csv",
    )
    fetch_observation_data(
        prec_numbers=["82"],
        type="daily",
        dates=None,
        months=[date(2022, 8, 1), date(2022, 9, 1)],
        csv_file_name="sample_daily.csv",
    )
    """
    service = ObservedDataProcessor(
        prec_numbers=prec_numbers,
        type=type,
        dates=dates,
        months=months,
    )
    service.save_observed_data(csv_file_name=csv_file_name)
