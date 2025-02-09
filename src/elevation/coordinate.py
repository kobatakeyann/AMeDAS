from math import atan, e, log, pi, tan


def lonlat_to_tile_coord(
    lon: float, lat: float, zoom_level: int
) -> tuple[int, int]:
    title_x = int((lon / 180 + 1) * 2**zoom_level / 2)
    tile_y = int(
        (
            (-log(tan((45 + lat / 2) * pi / 180)) + pi)
            * 2**zoom_level
            / (2 * pi)
        )
    )
    return title_x, tile_y


def tile_coord_to_northwest_lonlat(
    tile_x: int, tile_y: int, zoom_level: int
) -> tuple[float, float]:
    lon_left = (tile_x / 2.0**zoom_level) * 360 - 180
    map_y = (tile_y / 2.0**zoom_level) * 2 * pi - pi
    lat_upper = 2 * atan(e ** (-map_y)) * 180 / pi - 90
    return lon_left, lat_upper
