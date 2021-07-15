from abc import ABC, abstractmethod
from datetime import date
from src.utils.calendar import Frequency
from typing import Type, Sequence
from src.utils.interestrate import InterestRate
from src.instruments.cashflows import FixedCashFlow, FloatingCashFlow


class LinearInstrument(ABC):
    @abstractmethod
    def price(self):
        pass

    @abstractmethod
    def get_maturity(self):
        pass


class Deposit(LinearInstrument):
    def __init__(self, trade_date: date, settlement_date: date, maturity_date: date,
                 quote: float, notional: float, rate: Type[InterestRate]):
        self._trade_date = trade_date
        self._quote = quote
        cf1 = FixedCashFlow(settlement_date, settlement_date, settlement_date, -1.0*notional)
        cf2 = FixedCashFlow(settlement_date, maturity_date, maturity_date,
                            notional*rate.capitalization(settlement_date, maturity_date, quote))
        self._cfs = [cf1, cf2]
        self._ir = rate

    def __str__(self):
        ret = ['Deposit', 'TradeDate:' + str(self._trade_date), 'MaturityDate:' + str(self._cfs[1].payment_date),
               'Notional:' + '{:,.2f}'.format(-1*self._cfs[0].value), 'Rate:' + str(self._ir),
               'Quote:' + '{:,.4f}%'.format(100.*self._quote)] + [str(cf) for cf in self._cfs]
        return '\n'.join(ret)

    def price(self, **kwargs):
        return sum([kwargs['discounting'].df(cf.payment_date) * cf.value for cf in self._cfs])

    def get_maturity(self):
        return self._cfs[1].payment_date


class FRA(LinearInstrument):
    def __init__(self, trade_date: date, fixing_date: date, settlement_date: date, maturity_date: date,
                 quote: float, notional: float, rate: Type[InterestRate]):
        self._trade_date = trade_date
        self._fixing_date = fixing_date
        self._quote = quote
        fixcf1 = FixedCashFlow(settlement_date, settlement_date, settlement_date, -1.0 * notional)
        fixcf2 = FixedCashFlow(settlement_date, maturity_date, maturity_date,
                               notional * rate.capitalization(settlement_date, maturity_date, quote))
        flocf1 = FixedCashFlow(settlement_date, settlement_date, settlement_date, notional)
        flocf2 = FloatingCashFlow(settlement_date, maturity_date, settlement_date, maturity_date,
                                  settlement_date, rate, notional, True)
        self._fix_leg = [fixcf1, fixcf2]
        self._flo_leg = [flocf1, flocf2]

    def price(self, **kwargs):
        return sum([kwargs['discounting'].df(cf.payment_date) * cf.value for cf in self._fix_leg])

    def get_maturity(self):
        return self._fix_leg[1].payment_date


class IRS(LinearInstrument):
    def __init__(self, trade_date: date, quote: float,
                 fixed_leg_dates: Sequence[date], floating_leg_dates: Sequence[date],
                 fixed_leg_freq: Frequency, floating_leg_freq: Frequency):
        pass

    def price(self, **kwargs):
        pass

    def get_maturity(self):
        pass