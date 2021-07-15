from datetime import date


# class FloatingCashFlow(start: dt.datetime, end: dt.datetime, value: float)
#     self._start = start
#     self._end = end
#     self._value = value
#     self._notional = notional
#     self._interest_rate = interest_rate


class FixedCashFlow:
    def __init__(self, accrual_start: date, accrual_end: date, payment: date, value: float):
        self._acc_start = accrual_start
        self._acc_end = accrual_end
        self._value = value
        self._payment_date = payment

    @property
    def payment_date(self):
        return self._payment_date

    @property
    def value(self):
        return self._value

    def __str__(self):
        return '\t'.join([str(self._payment_date), '{:,.2f}'.format(self._value)])


class FloatingCashFlow:
    def __init__(self, fixing_start: date, fixing_end:date,
                accrual_start: date, accrual_end: date,
                payment: date, interest_rate,
                notional: float, is_notionaL_paid: bool,
                additive_margin = 0.0):
        self._fix_start = fixing_start
        self._fix_end = fixing_end
        self._acc_start = accrual_start
        self._acc_end = accrual_end
        self._payment_date = payment
        self._add_margin = additive_margin
        self._ir = interest_rate
        self._notional = notional
        self._is_notionaL_paid = is_notionaL_paid
        self._value = None

    def update_fixing(self, **kwargs):
        fixing = 0.0
        if 'fixing' in kwargs:
            fixing = kwargs['fixing']
        elif 'projection_curve' in kwargs:
            fixing = kwargs['projection_curve'].df(self._fix_start, self._fix_end, interest_rate=self._ir)
        if self._is_notionaL_paid:
            self._value = self._ir.capitalization(self._acc_start, self._acc_end, fixing + self._add_margin)
        else:
            self._value = self._ir.coupon(self._acc_start, self._acc_end, fixing + self._add_margin)
        self._value *= self._notional

    @property
    def payment_date(self):
        return self._payment_date

    @property
    def value(self):
        return self._value
