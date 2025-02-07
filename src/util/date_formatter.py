from datetime import date


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
