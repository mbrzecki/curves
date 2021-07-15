from src.utils.calendar import Calendar, DayRollingConvention, Frequency
import src.utils.interestrate as ir
from dateutil import parser
import src.instruments.factories as fs
import json


def prepare_instruments(json_file):
    with open(json_file) as js:
        d = json.load(js)
    as_of_date = parser.parse(d['Date']).date()
    calendar = Calendar(DayRollingConvention.parse(d['DayRollingConvention']), d['SpotLag'], *d['Holidays'])
    calendarz = calendar.generate_schedule(as_of_date, Frequency.Quarterly, "2Y")
    depo_ir = ir.InterestRate(ir.YearFraction.parse(d['Deposit']['YF']),
                              ir.Compounding.parse(d['Deposit']['Compounding']))
    depo_fact = fs.deposit_factory(calendar, depo_ir, as_of_date)

    fra_ir = ir.InterestRate(ir.YearFraction.parse(d['FRA']['YF']),
                              ir.Compounding.parse(d['FRA']['Compounding']))
    fra_fact = fs.fra_factory(calendar, fra_ir, as_of_date)

    deps = [depo_fact(quote, tenor) for tenor, quote in d['Deposit']['Quotes'].items()]
    fras = []
    for tenors, quote in d['FRA']['Quotes'].items():
        tenor1, tenor2 = tenors.split('x')
        fras.append(fra_fact(quote, tenor1+'M', tenor2+'M'))
    return {'Date': as_of_date,
            "Instruments": sorted(deps+fras,key=lambda i:i.get_maturity())}

def transform_fra_tenors(tenor, which_tenor):
    return tenor.split('x')[which_tenor]