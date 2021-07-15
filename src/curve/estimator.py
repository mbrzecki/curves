import src.instruments.instruments as instr
from scipy.optimize import newton
import numpy as np
from src.curve.curve import InterpolatedCurve


class AlgebraicBootstrapper:
    def __init__(self):
        self._instruments = None
        self._as_of = None

    def bootstrap_curve(self, **kwargs):
        cfs = self._prepare_fixed_cfs(kwargs['AsOfDate'], kwargs['Instruments'])
        arr, dates = self._construct_matrix(cfs)
        dfs = self._solve(arr)
        return list(dates)[1:], list(dfs)[1:]

    @staticmethod
    def _prepare_fixed_cfs(as_of_date, instruments):
        lst_of_cfs = list()
        for n, i in enumerate(instruments):
            instrument_cfs = []
            if isinstance(i, instr.Deposit):
                instrument_cfs = i._cfs
            elif isinstance(i, instr.FRA):
                instrument_cfs = i._fix_leg
            else:
                raise BaseException("Unexpected instrument type: " + str(type(i)))
            for cf in instrument_cfs:
                lst_of_cfs.append((n, cf.payment_date, cf.value))
        return lst_of_cfs

    def _construct_matrix(self, cfs):
        dates = sorted(set([i[1] for i in cfs]))
        date_idx = dict(zip(dates, range(len(dates))))
        size = len(date_idx)
        ret = np.zeros((size, size))
        for cf in cfs:
            ret[cf[0]][date_idx[cf[1]]] = cf[2]
        ret[size-1][0] = 1.0
        return ret, dates

    def _solve(self, arr):
        res = np.array([0.0]*arr.shape[0])
        res[-1] = 1.0
        return np.linalg.solve(arr, res)


class RootFindingBootstrapper:
    def __init__(self):
        self._instruments = None
        self._as_of = None

    def bootstrap_curve(self, **kwargs):
        dates = [kwargs['AsOfDate']]
        Dfs = [1.0]
        for i in kwargs['Instruments']:
            func = self._calibration(i, dates, Dfs, **kwargs)
            res = newton(func, Dfs[-1])
        return dates, Dfs

    def _calibration(self, instrument, dates, DFs, **kwargs):
        dates.append(instrument.get_maturity())
        DFs.append(DFs[-1])

        def inner(df):
            DFs[-1] = df
            curve = InterpolatedCurve(AsOfDate=kwargs['AsOfDate'],
                                      InputTransformer=kwargs['InputTransformer'],
                                      InterestRate=kwargs['InterestRate'],
                                      Dates=dates,
                                      DFs=DFs,
                                      Interpolation=kwargs['Interpolation'])
            return instrument.price(discounting=curve)

        return inner