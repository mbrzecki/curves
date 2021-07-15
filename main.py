from src.utils.io import prepare_instruments
from src.curve.estimator import AlgebraicBootstrapper, RootFindingBootstrapper
from src.curve.curve import InterpolatedCurve
from src.curve.interpolator import InterpolateDF
import src.utils.interestrate as ir
from src.instruments.instruments import FRA


def main():
    data = prepare_instruments('data/example_instruments.json')

    interest_rate = ir.InterestRate(ir.YearFraction.ACT365(), ir.Compounding.Simple())
    curve = InterpolatedCurve(AsOfDate=data['Date'],
                              InputTransformer=InterpolateDF(),
                              InterestRate=interest_rate,
                              Instruments=data['Instruments'],
                              Bootstrapper=AlgebraicBootstrapper(),
                              Interpolation='linear')

    # for i in data['Instruments']:
    #     print(i.price(discounting=curve))

    curve2 = InterpolatedCurve(AsOfDate=data['Date'],
                               InputTransformer=InterpolateDF(),
                               InterestRate=interest_rate,
                               Instruments=data['Instruments'],
                               Bootstrapper=RootFindingBootstrapper(),
                               Interpolation='linear')


if __name__ == '__main__':
    main()
