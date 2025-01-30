from datetime import date


class DateArranger:
    def __init__(self, date: date) -> None:
        self.date = date

    def get_padded_date(self) -> tuple[str, str, str]:
        year, month, day = (
            str(self.date.year).zfill(4),
            str(self.date.month).zfill(2),
            str(self.date.day).zfill(2),
        )
        return (year, month, day)
