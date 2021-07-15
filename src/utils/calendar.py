from datetime import date, timedelta
from dateutil import easter, relativedelta
from enum import Enum
from typing import Type
from time import strptime
import os
import json


class Frequency(Enum):
    Monthly = 1
    Quarterly = 3
    Semiannually = 6
    Annually = 12

    @staticmethod
    def get_number_of_months(freq):
        if freq == Frequency.Monthly:
            return 1
        if freq == Frequency.Quarterly:
            return 3
        if freq == Frequency.Semiannually:
            return 6
        if freq == Frequency.Annually:
            return 12
        raise Exception('Unknown frequency')


class DayRollingConvention(Enum):
    Following = 1
    ModFollowing = 2
    Preceding = 3
    ModPreceding = 4

    @staticmethod
    def parse(drc):
        if drc == "Following":
            return DayRollingConvention.Following
        if drc == "Preceding":
            return DayRollingConvention.Preceding
        if drc == "ModFollowing":
            return DayRollingConvention.ModFollowing
        if drc == "ModPreceding":
            return DayRollingConvention.ModPreceding


class Calendar:
    def __init__(self, drc: Type[DayRollingConvention], spot_lag, *holidays):
        self._drc = drc
        self._fixed_holidays = set()
        self._moving_holidays = []
        self._spot_lag = spot_lag
        if self. _drc == DayRollingConvention.Preceding:
            self._apply_day_rolling_convention = self._preceding
        elif self. _drc == DayRollingConvention.ModPreceding:
            self._apply_day_rolling_convention = self._mod_preceding
        elif self. _drc == DayRollingConvention.Following:
            self._apply_day_rolling_convention = self._following
        elif self. _drc == DayRollingConvention.ModFollowing:
            self._apply_day_rolling_convention = self._mod_following

        for hol in holidays:
            with open(os.path.join('data', 'holidays', hol+'.json')) as jsfile:
                d = json.load(jsfile)
                for fh in d['Fixed']:
                    t = fh.split(' ')
                    self._fixed_holidays.add((strptime(t[0], '%b').tm_mon, int(t[1])))
                for mh in d['Moving']:
                    if mh == 'Whit Monday':
                        self._moving_holidays.append(Calendar._easter_related_holiday(50))
                    elif mh == 'Easter Monday':
                        self._moving_holidays.append(Calendar._easter_related_holiday(1))
                    elif mh == 'Good Friday':
                        self._moving_holidays.append(Calendar._easter_related_holiday(-2))
                    elif mh == 'Corpus Christi':
                        self._moving_holidays.append(Calendar._easter_related_holiday(60))

    def is_weekday(self, d: date):
        return d.weekday() < 5 and not self.is_holiday(d)

    def is_holiday(self, d: date):
        return (d.month, d.day) in self._fixed_holidays or any(map(lambda f: f(d), self._moving_holidays))

    def apply_tenor(self, d: date, tenor):
        if tenor == "ON":
            return self.add_working_days(d, 1)
        elif tenor == "TN":
            return self.add_working_days(d, 2)
        elif tenor == "Spot":
            return self.add_working_days(d, self._spot_lag)

        n, unit = int(tenor[:-1]), tenor[-1:]
        d = self.add_working_days(d, self._spot_lag)
        if unit == "W":
            d += timedelta(weeks=n)
        elif unit == "M":
            d += relativedelta.relativedelta(months=n)
        elif unit == "Q":
            d += relativedelta.relativedelta(months=3*n)
        elif unit == "Y":
            d += relativedelta.relativedelta(years=n)
        return self._apply_day_rolling_convention(d)

    def calculate_fixing(self, d: date):
        return self.add_working_days(d, -1*self._spot_lag)

    def add_working_days(self, d: date, n: int):
        iterator = 0
        ret = d
        increment = 1 if n > 0 else -1
        while iterator < abs(n):
            ret += timedelta(days=increment)
            if self.is_weekday(ret):
                iterator += 1
        return ret

    def generate_schedule(self, d: date, freq: Frequency, tenor: str):
        nmonts = Frequency.get_number_of_months(freq)
        mat = self.apply_tenor(d, tenor)
        ret = [self.apply_tenor(d, "Spot")]
        n = 0
        while ret[-1] < mat:
            n += nmonts
            ret.append(self.apply_tenor(d, str(n)+'M'))
        return ret

    def _apply_day_rolling_convention(self, d: date):
        # should be set in constructor
        raise Exception("Day rolling not set")

    def _preceding(self, d):
        if not self.is_weekday(d):
            return self.add_working_days(d, -1)
        return d

    def _following(self, d):
        if self.is_holiday(d):
            return self.add_working_days(d, 1)
        return d

    def _mod_preceding(self, d):
        if self.is_weekday(d):
            return d
        temp = self.add_working_days(d, -1)
        return temp if temp.month == d.month else self.add_working_days(d, 1)

    def _mod_following(self, d):
        if self.is_weekday(d):
            return d
        temp = self.add_working_days(d, 1)
        return temp if temp.month == d.month else self.add_working_days(d, -1)

    @staticmethod
    def _easter_related_holiday(day_shift: int):
        def inner(d: date):
            holiday_date = easter.easter(d.year) + timedelta(days=day_shift)
            return holiday_date == d
        return inner
