from math import cos, radians, sin
from typing import NamedTuple

import numpy as np

from constants.missing_value import MISSING_VALUE


class WindComponents(NamedTuple):
    u: float
    v: float


def get_wind_components(
    wind_speed: float, wind_direction: float
) -> WindComponents:
    if wind_speed == -888.8:
        return WindComponents(u=0, v=0)
    if wind_speed == np.nan or wind_direction == float(MISSING_VALUE):
        return WindComponents(u=np.nan, v=np.nan)
    u = wind_speed * (-sin(radians(wind_direction)))
    v = wind_speed * (-cos(radians(wind_direction)))
    return WindComponents(u=u, v=v)
