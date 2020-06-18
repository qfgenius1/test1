###############################################################################
#
#                                 NOTICE:
#  THIS PROGRAM CONSISTS OF TRADE SECRECTS THAT ARE THE PROPERTY OF
#  Advanced Products Ltd. THE CONTENTS MAY NOT BE USED OR DISCLOSED
#  WITHOUT THE EXPRESS WRITTEN PERMISSION OF THE OWNER.
#
#               COPYRIGHT Advanced Products Ltd 2016-2019
#
###############################################################################

import QuantLib as ql
import json

def write_out_data(run_name, type, price, time_taken, step):
    output_data = json.loads('{}')
    output_data['run_name'] = run_name
    output_data['type'] = type
    output_data['price'] = str(price)
    output_data['step'] = str(step)
    output_data['time_taken'] = str(time_taken)
    return output_data


def read_data_and_get_process(input_data):
    # option data
    maturity_date = get_ql_date(input_data['maturity'])
    spot_price = float(input_data['spot_price'])
    strike_price = float(input_data['strike_price'])
    volatility = float(input_data['volatility'])
    risk_free_rate = float(input_data['rate'])
    calculation_date = get_ql_date(input_data['price_date'])

    # get process
    bsm_process = set_up_option(maturity_date, spot_price, strike_price, volatility, risk_free_rate, calculation_date)
    return bsm_process

def get_ql_date(string_date):
    # date format is DD/MM/YYYY
    date_tokens = string_date.split('/')
    year = int(date_tokens[2])
    month = int(date_tokens[1])
    day = int(date_tokens[0])

    return ql.Date(day, month, year)

def binomial_price(bsm_process, steps):
    european_option = bsm_process.option

    binomial_engine = ql.BinomialVanillaEngine(bsm_process, "crr", steps)
    european_option.setPricingEngine(binomial_engine)
    return european_option.NPV()

def finite_differences_price(bsm_process, timesteps , grid_points):
    european_option = bsm_process.option

    fdEngine = ql.FdBlackScholesVanillaEngine(bsm_process, timesteps, grid_points)
    european_option.setPricingEngine(fdEngine)
    return european_option.NPV()

def analytic_price(bsm_process):
    european_option = bsm_process.option

    european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    bs_price = european_option.NPV()
    return bs_price

def set_up_option(maturity_date, spot_price, strike_price, volatility, risk_free_rate, calculation_date):
    # assume no dividend
    dividend_rate =  0.0
    option_type = ql.Option.Call
    day_count = ql.Actual365Fixed()
    calendar = ql.UnitedStates()

    ql.Settings.instance().evaluationDate = calculation_date
    # construct the European Option
    payoff = ql.PlainVanillaPayoff(option_type, strike_price)
    exercise = ql.EuropeanExercise(maturity_date)
    european_option = ql.VanillaOption(payoff, exercise)
    spot_handle = ql.QuoteHandle(
        ql.SimpleQuote(spot_price)
    )
    flat_ts = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, risk_free_rate, day_count)
    )
    dividend_yield = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, dividend_rate, day_count)
    )
    flat_vol_ts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(calculation_date, calendar, volatility, day_count)
    )
    bsm_process = ql.BlackScholesMertonProcess(spot_handle, 
                                               dividend_yield, 
                                               flat_ts, 
                                               flat_vol_ts)
    bsm_process.option = european_option

    return bsm_process

