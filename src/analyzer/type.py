from pydantic import BaseModel


class ObservedValuesContainer(BaseModel, frozen=True):
    block_no: str
    value: float
    lon: float
    lat: float
