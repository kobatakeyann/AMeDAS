from datetime import date, datetime


class PaddedDate:
    def __init__(self, date: date) -> None:
        self._date = date

    @property
    def year(self) -> str:
        return f"{self._date.year:04d}"

    @property
    def month(self) -> str:
        return f"{self._date.month:02d}"

    @property
    def day(self) -> str:
        return f"{self._date.day:02d}"


class PaddedDatetime:
    def __init__(self, datetime: datetime) -> None:
        self._datetime = datetime

    @property
    def year(self) -> str:
        return f"{self._datetime.year:04d}"

    @property
    def month(self) -> str:
        return f"{self._datetime.month:02d}"

    @property
    def day(self) -> str:
        return f"{self._datetime.day:02d}"

    @property
    def hour(self) -> str:
        return f"{self._datetime.hour:02d}"

    @property
    def minute(self) -> str:
        return f"{self._datetime.minute:02d}"
