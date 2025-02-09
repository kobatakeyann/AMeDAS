def format_lon_ticks(lon: float, _) -> str:
    degrees = int(lon)
    minutes = abs(int((lon - degrees) * 60))
    if minutes == 0:
        minutes = "00"
    return f"{degrees}°{minutes}'E"


def format_lat_ticks(lat: float, _) -> str:
    degrees = int(lat)
    minutes = abs(int((lat - degrees) * 60))
    if minutes == 0:
        minutes = "00"
    return f"{degrees}°{minutes}'N"
