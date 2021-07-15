from scipy.interpolate.interpolate import interp1d


class Curve:
    pass


class InterpolatedCurve:
    def __init__(self, **kwargs):
        self._as_of_date = kwargs['AsOfDate']
        self._input_transformer = kwargs['InputTransformer']
        self._interest_rate = kwargs['InterestRate']
        self._interpolation_type = kwargs['Interpolation']

        self._dfs = []
        self._dates = []

        if 'DFs' in kwargs and 'Dates' in kwargs:
            self._dfs = kwargs['DFs']
            self._dates = kwargs['Dates']
        elif 'Bootstrapper' in kwargs and 'Instruments' in kwargs:
            self._dates, self._dfs = kwargs['Bootstrapper'].bootstrap_curve(**kwargs)

        self._ts = [self._interest_rate.yf(self._as_of_date, d) for d in self._dates]
        self._inputs = [self._input_transformer.get_input(df, self._interest_rate, self._as_of_date, d)
                        for df, d in zip(self._dfs, self._dates)]
        self._interpolator = interp1d(self._ts, self._inputs, kind=kwargs['Interpolation'], copy=False)

    def df(self, date):
        if date < self._as_of_date:
            return 0.0
        if date == self._as_of_date:
            return 1.0
        if date <= self._dates[-1]:
            return self._interpolator(self._interest_rate.yf(self._as_of_date, date))
        raise BaseException("No extrapolation implemented")

    def __str__(self):
        ret = ['InterpolatedCurve',
               'AsOfDate: ' + str(self._as_of_date),
               'InterestRate: ' + str(self._interest_rate),
               'Interpolation: ' + self._interpolation_type + ' ' +  str(self._input_transformer)]
        for d, df in zip(self._dates, self._dfs):
            ret.append(str(d) + '\t' + '{0:.8f}'.format(df))
        return '\n'.join(ret)
