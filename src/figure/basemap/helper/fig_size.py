from config.figure.base_map import LAT_BOTTOM, LAT_TOP, LON_LEFT, LON_RIGHT


def calculate_figsize() -> tuple[int, float]:
    lat_dif = LAT_TOP - LAT_BOTTOM
    lon_dif = LON_RIGHT - LON_LEFT
    figsize = (8, 8 * float(float(lat_dif) / float(lon_dif)))
    return figsize
