from datetime import date
from src.instruments.instruments import Deposit, FRA


def deposit_factory(calendar, interest_rate, as_of: date):
    def inner(quote, tenor, notional=100.0):
        start_date = as_of if tenor == 'ON' else \
                    calendar.apply_tenor(as_of, 'ON') if tenor == 'TN' else \
                    calendar.apply_tenor(as_of, 'Spot')
        maturity_date = calendar.apply_tenor(as_of, tenor)
        return Deposit(as_of, start_date, maturity_date, quote, notional, interest_rate)

    return inner


def fra_factory(calendar, interest_rate, as_of: date):
    def inner(quote, tenor1, tenor2, notional=100.0):
        settlement_date = calendar.apply_tenor(as_of, tenor1)
        fixing_date = calendar.calculate_fixing(settlement_date)
        maturity_date = calendar.apply_tenor(as_of, tenor2)
        return FRA(as_of, fixing_date, settlement_date, maturity_date, quote, notional, interest_rate)

    return inner
