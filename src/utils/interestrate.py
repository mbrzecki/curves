import datetime as dt


class YearFraction:
    @staticmethod
    def parse(yf: str):
        if yf == 'ACT365':
            return YearFraction.ACT365()

    class ACT365:
        def __call__(self, start: dt.date, end: dt.date):
            return (end - start).days / 365.0

        def __str__(self):
            return 'ACT365'


class Compounding:
    @staticmethod
    def parse(comp: str):
        if comp == 'Simple':
            return Compounding.Simple()

    class Simple:
        def df(self, accrual_period: float, rate: float):
            return 1.0 / (1 + accrual_period * rate)

        def rate(self, accrual_period: float, future_value: float):
            return (future_value - 1.0) / accrual_period

        def __str__(self):
            return 'Simple'


class InterestRate:
    def __init__(self, year_fraction, compounding):
        self._yf = year_fraction
        self._comp = compounding

    def yf(self, start_date: dt.date, end_date: dt.date):
        return self._yf(start_date, end_date)

    def df(self, start: dt.datetime, end: dt.datetime, rate: float):
        return self._comp.df(self._yf(start, end), rate)

    def capitalization(self, start: dt.datetime, end: dt.datetime, rate: float):
        return 1.0 / self.df(start, end, rate)

    def coupon(self, start: dt.datetime, end: dt.datetime, rate: float):
        return self.capitalization(start, end, rate) - 1.0

    def rate(self, start: dt.datetime, end: dt.datetime, future_value: float):
        return self._comp.rate(self._yf(start, end), future_value)

    def forward_rate(self, start: dt.datetime, end: dt.datetime, df_start: float, df_end: float):
        return self._comp.rate(self._yf(start, end), df_start / df_end)

    def __str__(self):
        return str(self._comp) + ' ' + str(self._yf)
