from io import StringIO
from urllib.error import HTTPError

import numpy as np
import pandas as pd

from api.data_fetcher import fetch_data
from elevation.coordinate import (
    lonlat_to_tile_coord,
    tile_coord_to_northwest_lonlat,
)


class Elevation:
    def __init__(
        self,
        lon_left: float,
        lon_right: float,
        lat_bottom: float,
        lat_top: float,
        zoom_level: int,
    ) -> None:
        self._x_upper_left, self._y_upper_left = lonlat_to_tile_coord(
            lon_left, lat_top, zoom_level
        )
        self._x_lower_right, self._y_lower_right = lonlat_to_tile_coord(
            lon_right, lat_bottom, zoom_level
        )
        self._zoom_level = zoom_level

    def get_elevation_array(self, tile_x: int, tile_y: int) -> np.ndarray:
        """Get elevation array of one tile from Geographical Survey Institute.

        Args:
            tile_x (int): x-coodinate in Tile Coordinates
            tile_y (int): y-coodinate in Tile Coordinates
            zoom_level (int): Zoom level in Tile Coordinates

        Returns:
            np.ndarray: elevation array of the tile designated by coordinate(x,y)
        """
        url = f"http://cyberjapandata.gsi.go.jp/xyz/dem/{self._zoom_level}/{tile_x}/{tile_y}.txt"
        try:
            res_data = fetch_data(url)
            text_data = res_data.decode("utf-8")
            elevation_text = text_data.replace("e", "0.0")
            elevation_df = pd.read_csv(StringIO(elevation_text), header=None)
            return elevation_df.values
        except HTTPError as http_err:
            if http_err.code == 404:
                return np.zeros((256, 256))
            raise HTTPError(
                http_err.url,
                http_err.code,
                http_err.reason,
                http_err.headers,
                http_err.fp,
            )

    def get_concatted_array(self) -> np.ndarray:
        array_concatted_in_x = np.array([])
        for x in range(self._x_upper_left, self._x_lower_right + 1):
            array_concatted_in_y = np.array([])
            for y in range(self._y_upper_left, self._y_lower_right + 1):
                elevation = self.get_elevation_array(x, y)
                if len(array_concatted_in_y) == 0:
                    array_concatted_in_y = elevation
                else:
                    array_concatted_in_y = np.append(
                        array_concatted_in_y, elevation, 0
                    )
            if len(array_concatted_in_x) == 0:
                array_concatted_in_x = array_concatted_in_y
            else:
                array_concatted_in_x = np.append(
                    array_concatted_in_x, array_concatted_in_y, 1
                )
        self.elevation_array = array_concatted_in_x
        return self.elevation_array

    def get_coordinates_for_plot(self) -> tuple[np.ndarray, ...]:
        lon_left_edge, lat_top_edge = tile_coord_to_northwest_lonlat(
            self._x_upper_left, self._y_upper_left, self._zoom_level
        )
        lon_right_edge, lat_bottom_edge = tile_coord_to_northwest_lonlat(
            self._x_lower_right + 1, self._y_lower_right + 1, self._zoom_level
        )
        num_x = self.elevation_array.shape[1]
        num_y = self.elevation_array.shape[0]
        lon_deviation = ((lon_right_edge - lon_left_edge) / num_x) * 0.5
        lat_deviation = ((lat_top_edge - lat_bottom_edge) / num_y) * 0.5
        lon_coords = np.linspace(
            lon_left_edge + lon_deviation,
            lon_right_edge + lon_deviation,
            num_x,
        )
        lat_coords = np.linspace(
            lat_top_edge + lat_deviation,
            lat_bottom_edge + lat_deviation,
            num_y,
        )
        return np.meshgrid(lon_coords, lat_coords)
