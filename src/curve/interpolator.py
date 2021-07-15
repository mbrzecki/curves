from abc import ABC, abstractmethod
from datetime import date


class InterpolationInput(ABC):
    @abstractmethod
    def get_input(self, df: float, rate, start_date: date, end_date: date):
        raise BaseException("Not implemented")

    @abstractmethod
    def get_df(self, x: float, rate, start_date: date, end_date: date):
        raise BaseException("Not implemented")

    @abstractmethod
    def __str__(self):
        raise BaseException("Not implemented")

class InterpolateDF(InterpolationInput):
    def get_input(self, df: float, rate, start_date: date, end_date: date):
        return df

    def get_df(self, x: float, rate, start_date: date, end_date: date):
        return x

    def __str__(self):
        return 'DF'


class InterpolateInverseDF(InterpolationInput):
    def get_input(self, df: float, rate, start_date: date, end_date: date):
        return 1.0 / df

    def get_df(self, x: float, rate, start_date: date, end_date: date):
        return 1.0 / x

    def __str__(self):
        return 'Inverse DF'

class InterpolateZCR(InterpolationInput):
    def get_input(self, df: float, rate, start_date: date, end_date: date):
        return rate.rate(start_date, end_date, 1.0 / df)

    def get_df(self, x: float, rate, start_date: date, end_date: date):
        return rate.df(start_date, end_date, x)

    def __str__(self):
        return 'ZeroCouponRate'