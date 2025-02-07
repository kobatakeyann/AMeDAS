from pydantic import BaseModel


class RectangleArea(BaseModel, frozen=True):
    lon_left: float
    lon_right: float
    lat_bottom: float
    lat_top: float
