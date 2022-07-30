import os
from os import environ
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import configparser
import os
from urllib.request import urlopen
import json
from io import StringIO

# from app_utility import settings
from app_utility import company_valuation as cv
# from app_utility import stock_time_series as sts

from matplotlib.font_manager import FontProperties
fontP = FontProperties()
fontP.set_size('small')

cfile = os.path.join(os.path.dirname(__file__), 'config.ini')
cfg = configparser.ConfigParser()
cfg.read(cfile)

try:
    cfg.has_section('API')
except:
    raise Exception('Config File was not read.')

def get_urlroot():
    urlroot = "https://fmpcloud.io/api/v3/"
    return urlroot

def get_urlrootfmp():
    urlrootfmp = "https://financialmodelingprep.com/api/v3/"
    return urlrootfmp

def get_apikey():
    apikey = "66282407a363585efee4a4f1643e026f"
    return apikey

def set_apikey(apikey):
    cfg['API']['api_key'] = apikey
    with open(cfile, 'w') as configfile:
        cfg.write(configfile)

def safe_read_json(data):
    if (data.find("Error Message") != -1):
        raise Exception(data[20:-3])
    else:
        return pd.read_json((data))
        # return pd.read_json(StringIO(data))


def historical_stock_data(ticker, period = None, dailytype = None, last = None, start = None, end = None):
    """Historical stock data API for . From https://fmpcloud.io/documentation#historicalStockData

    Input:
        ticker - fx for which you want the historical data
        period - tick periodicity - can be '1min', '5min', '15min', '30min', '1hour'. Defaults to '15min'. Do not use with daily type
        dailytype - can be 'line', 'change'. line chart info for daily price or daily change and volume. Do not use with period.
        last - fx data for last x days. Only works with dailytype. Does not work with period
        start - start date in the format yyyy-mm-dd. eg: '2018-01-01'
        end - end date in the format yyyy-mm-dd. eg: '2019-01-01'
    Returns:
        Dataframe -- fx stock data
    """
    urlroot = get_urlroot()
    apikey = get_apikey()
    if ((dailytype is not None) or (last is not None)) and (period is not None):
        raise Exception(" 'period' and 'dailytype' cannot be set on the same call. Please choose either, not both. 'last' can only be set with 'dailytype'")
    if dailytype is not None:
        urlhist = urlroot + 'historical-price-full/' + ticker.upper() + '?'
    elif period is not None:
        urlhist = urlroot + 'historical-chart/' + period + '/' + ticker.upper() + '?'
    else:
        raise Exception("'period' or 'dailytype' not set. Please set atleast one")
    if dailytype == 'line':
        urlhist = urlhist + "serietype=line"
    if last is not None:
        urlhist = urlhist + "&timeseries=" + str(last)
    if (last is None) and (start is not None):
        urlhist = urlhist + "&from=" + start
    if (last is None) and (end is not None):
        urlhist = urlhist + "&to" + end
    url = urlhist+ "&apikey=" + apikey
    response = urlopen(url)
    data = response.read().decode("utf-8")
    data = safe_read_json(data)
    if dailytype is not None:
        datatick = data['symbol']
        data_mod = pd.DataFrame.from_records(data['historical'])
        data_mod['symbol'] = datatick
        data = data_mod
    data['date'] = pd.to_datetime(data['date'], format = '%Y-%m-%d %H:%M:%S')
    data = data.set_index('date')
    return data

def financial_ratios(ticker, period = 'annual', ttm = False):
    """Financial Ratios API from https://fmpcloud.io/documentation#financialRatios

    Input:
        ticker : ticker for which we need the financial ratios
        period : 'annual', 'quarter'. Periodicity of requested balance sheet. Defaults to annual
        ttm: trailing twelve months financial ratios. Default is False
    Returns:
        Financial ratios info for selected ticker
    """
    urlroot = get_urlroot()
    apikey = get_apikey()
    if ttm:
        typeurl = "ratios-ttm/"
    else:
        typeurl = "ratios/"

    url = urlroot + typeurl + ticker.upper() + "?" + "period=" + period + "&apikey=" + apikey
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return safe_read_json(data)

def key_metrics(ticker, period = 'annual'):
    """Key Metrics API from https://fmpcloud.io/documentation#keyMetrics

    Input:
        ticker : ticker for which we need the key metrics
        period : 'annual', 'quarter'. Periodicity of requested balance sheet. Defaults to annual
    Returns:
        Key metrics info for selected ticker
    """
    urlroot = get_urlroot()
    apikey = get_apikey()
    typeurl = "key-metrics/"

    url = urlroot + typeurl + ticker.upper() + "?" + "period=" + period + "&apikey=" + apikey
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return safe_read_json(data)

def enterprise_value(ticker, period = 'annual'):
    """Enterprise value API from https://fmpcloud.io/documentation#enterpriseValue

    Input:
        ticker : ticker for which we need the enterprise value
        period : 'annual', 'quarter'. Periodicity of requested balance sheet. Defaults to annual
    Returns:
        Enterprise value info for selected ticker
    """
    urlroot = get_urlroot()
    apikey = get_apikey()
    typeurl = "enterprise-values/"

    url = urlroot + typeurl + ticker.upper() + "?" + "period=" + period + "&apikey=" + apikey
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return safe_read_json(data)

def income_statement(ticker, period = 'annual', ftype = 'full'):
    """Income statement API from https://fmpcloud.io/documentation#incomeStatement

    Input:
        ticker : ticker for which we need the income statement
        period : 'annual', 'quarter'. Periodicity of requested balance sheet. Defaults to annual
        ftype : 'full', 'growth'. Defines input sheet type. Defaults to full.
    Returns:
        Income statement info for selected ticker
    """
    urlroot = get_urlroot()
    apikey = get_apikey()
    typeurl = ''
    try:
        if ftype == 'full':
            typeurl = 'income-statement/'
        elif ftype == 'growth':
            typeurl = 'income-statement-growth/'
#        elif bstype == 'short':
#            typeurl = 'income-statement-shorten/'
#        elif bstype == 'growth-short':
#            typeurl = 'income-statement-growth-shorten/'
    except KeyError:
        raise KeyError('Income statement type not correct')

    url = urlroot + typeurl + ticker.upper() + "?" + "period=" + period + "&apikey=" + apikey
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return safe_read_json(data)

def cash_flow_statement(ticker, period = 'annual', ftype = 'full'):
    """Cash Flow Statement API from https://fmpcloud.io/documentation#cashFlowStatement

    Input:
        ticker : ticker for which we need the cash flow statement
        period : 'annual', 'quarter'. Periodicity of requested balance sheet. Defaults to annual
        ftype : 'full', 'growth'. Defines input sheet type. Defaults to full.
    Returns:
        Income statement info for selected ticker
    """
    urlroot = get_urlroot()
    apikey = get_apikey()
    typeurl = ''
    try:
        if ftype == 'full':
            typeurl = 'cash-flow-statement/'
        elif ftype == 'growth':
            typeurl = 'cash-flow-statement-growth/'
#        elif bstype == 'short':
#            typeurl = 'income-statement-shorten/'
#        elif bstype == 'growth-short':
#            typeurl = 'income-statement-growth-shorten/'
    except KeyError:
        raise KeyError('Cash Flow Statement type not correct')

    url = urlroot + typeurl + ticker.upper() + "?" + "period=" + period + "&apikey=" + apikey
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return safe_read_json(data)

def dcf(ticker, history = 'today'):
    """Discounted Cash Flow Valuation API from https://fmpcloud.io/documentation#dcf

    Input:
        ticker : ticker for which we need the dcf
        history: 'today','daily', 'quarter', 'annual'. Periodicity of requested DCF valuations. Defaults to single value of today
    Returns:
        Discounted Cash Flow Valuation info for selected ticker
    """
    urlroot = get_urlroot()
    apikey = get_apikey()
    try:
        if history == 'today':
            typeurl = 'discounted-cash-flow/'
            url = urlroot + typeurl + ticker.upper() + "?" + "apikey=" + apikey
        elif history == 'daily':
            typeurl = 'historical-daily-discounted-cash-flow/'
            url = urlroot + typeurl + ticker.upper() + "?" + "apikey=" + apikey
        elif history == 'annual':
            typeurl = 'historical-discounted-cash-flow-statement/'
            url = urlroot + typeurl + ticker.upper() + "?" + "apikey=" + apikey
        elif history == 'quarter':
            typeurl = 'historical-discounted-cash-flow-statement/'
            url = urlroot + typeurl + ticker.upper() + "?" + "period=" + history + "&apikey=" + apikey
    except KeyError:
        raise KeyError('Discounted Cash Flow history requested not correct. ' + history + ' is not an accepted key')
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return safe_read_json(data)

def market_capitalization(ticker, history = 'today'):
    """Market Capitalization API from https://fmpcloud.io/documentation#marketCapitalization

    Input:
        ticker : ticker for which we need the Market Cap
        history: 'today','daily'. Periodicity of requested Market Caps. Defaults to single value of today
    Returns:
        Market Cap info for selected ticker
    """
    urlroot = get_urlroot()
    apikey = get_apikey()
    try:
        if history == 'today':
            typeurl = 'market-capitalization/'
        elif history == 'daily':
            typeurl = 'historical-market-capitalization/'
    except KeyError:
        print('Market Cap history requested not correct')
    url = urlroot + typeurl + ticker.upper() + "?" + "apikey=" + apikey
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return safe_read_json(data)

def balance_sheet(ticker, period = 'annual', ftype = 'full'):
    """Balance sheet API from https://fmpcloud.io/documentation#balanceSheet

    Input:
        ticker : ticker for which we need the balance sheet values
        period : 'annual', 'quarter'. Periodicity of requested balance sheet. Defaults to annual
        ftype : 'full', 'growth'. Defines input sheet type. Defaults to full.
    Returns:
        Balance sheet info for selected ticker
    """
    urlroot = get_urlroot()
    apikey = get_apikey()
    typeurl = ''
    try:
        if ftype == 'full':
            typeurl = 'balance-sheet-statement/'
        elif ftype == 'growth':
            typeurl = 'balance-sheet-statement-growth/'
#        elif ftype == 'short':
#            typeurl = 'balance-sheet-statement-shorten/'
#        elif ftype == 'growth-short':
#            typeurl = 'balance-sheet-statement-growth-shorten/'
    except KeyError:
        print('Balance sheet type not correct')

    url = urlroot + typeurl + ticker.upper() + "?" + "&period=" + period + "&apikey=" + apikey
    x_y="https://fmpcloud.io/api/v3/balance-sheet-statement/AAPL?limit=120&apikey=YOUR_API_KEY"
    st.write('this is what it should look like',x_y)
    st.write('check url',url)
    response = urlopen(url)
    data = response.read().decode("utf-8")
    data = safe_read_json(url)
    st.write(data)
    return data

today = datetime.today()
todaystr = today.strftime("%Y-%m-%d")
ten_years_ago = datetime.today() - timedelta(days=10*365)
ten_years_ago_str = ten_years_ago.strftime("%Y-%m-%d")
one_years_ago = datetime.today() - timedelta(days=1*365)
one_years_ago_str = one_years_ago.strftime("%Y-%m-%d")


years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')



st.title('Fundamentals')

st.sidebar.title("Setup")
st.sidebar.write("Please get your FMP API key here [link](https://financialmodelingprep.com/developer)")
api_key = st.sidebar.text_input('API Key', '', type="password")

try:
    if environ.get('fmp_key') is not None:
        set_apikey(os.environ['fmp_key'])
except:
    set_apikey(api_key)

symbol_search = st.sidebar.text_input('Symbol', 'AAPL')
#df_ticker = sts.ticker_search(match = symbol_search)

#scroll_list = list(df_ticker.name.values)
#scroll_list.append(symbol_search)

#selected = st.sidebar.selectbox('symbols found', scroll_list)


# http://www.beatthemarketanalyzer.com/blog/sp-400-mid-cap-stock-tickers-list/
# https://github.com/JavierCastilloGuillen/Market_Screener/blob/master/screener_csv.py



if st.sidebar.button("Start"):

    symbol = symbol_search
    #df_ticker.loc[df_ticker['name'] == selected,'symbol'][0]

    st.write('showing results for:', symbol)

    # get historical prices
    df_prices_ = historical_stock_data(symbol, dailytype = 'line', start = one_years_ago_str, end =todaystr)
    df_prices = df_prices_.reset_index().set_index('date')
    st.write('df_prices',df_prices.head())
    # get financial ratios

    df_balance_sheet = balance_sheet(ticker =symbol, period = 'annual').set_index('date')
    st.write('working up to here')
    st.write('df_balance sheet',df_balance_sheet.head())

    df_ratios = financial_ratios(ticker=symbol,period='annual',ttm = False).set_index('date')
    st.write('df_ratios',df_ratios.head())
    # get performance metrics
    df_metrics = key_metrics(ticker =symbol, period = 'annual').set_index('date')
    st.write('df_metrics',df_metrics.head())
    # get income statement
    df_income = income_statement(ticker = symbol, period = 'annual', ftype = 'full').set_index('date')
    st.write('df_income',df_income.head())
    # df_enterprise = enterprise_value(ticker =symbol, period = 'annual').set_index('date')
    # st.write('df_enterprise',df_enterprise.head())
    st.write('Is balance sheet working??')


    test_concat=pd.concat([df_prices,df_ratios,df_metrics,df_income,df_balance_sheet])
    st.write(test_concat)


    # get cashflow statement
    # df_cashflow = cash_flow_statement(ticker = symbol, period = 'annual', ftype = 'full')
    # get discounted cash_flow_statement
    # df_dcf = dcf(ticker = symbol, history = 'annual')

    # except:
    #     st.write("Stock data unavailable!")



    # try:
    #     symbol = symbol_search
    #     #df_ticker.loc[df_ticker['name'] == selected,'symbol'][0]

    #     st.write('showing results for:', symbol)

    #     # get historical prices
    #     df_prices_ = historical_stock_data(symbol, dailytype = 'line', start = one_years_ago_str, end =todaystr)
    #     df_prices = df_prices_.reset_index().set_index('date')
    #     st.write('df_prices',df_prices.head())
    #     # get financial ratios

    #     df_balance_sheet = balance_sheet(ticker =symbol, period = 'annual').set_index('date')
    #     st.write('working up to here')
    #     st.write('df_balance sheet',df_balance_sheet.head())

    #     df_ratios = financial_ratios(ticker=symbol,period='annual',ttm = False).set_index('date')
    #     st.write('df_ratios',df_ratios.head())
    #     # get performance metrics
    #     df_metrics = key_metrics(ticker =symbol, period = 'annual').set_index('date')
    #     st.write('df_metrics',df_metrics.head())
    #     # get income statement
    #     df_income = income_statement(ticker = symbol, period = 'annual', ftype = 'full').set_index('date')
    #     st.write('df_income',df_income.head())
    #     # df_enterprise = enterprise_value(ticker =symbol, period = 'annual').set_index('date')
    #     # st.write('df_enterprise',df_enterprise.head())
    #     st.write('Is balance sheet working??')


    #     test_concat=pd.concat([df_prices,df_ratios,df_metrics,df_income,df_balance_sheet])
    #     st.write(test_concat)


    #     # get cashflow statement
    #     # df_cashflow = cash_flow_statement(ticker = symbol, period = 'annual', ftype = 'full')
    #     # get discounted cash_flow_statement
    #     # df_dcf = dcf(ticker = symbol, history = 'annual')

    # except:
    #     st.write("Stock data unavailable!")

stocks=pd.read_excel('C:/Users/Darragh/Documents/Python/finance_ratios/ticker_select.xlsx')
# st.write(stocks['Ticker'])

# for symbol in stocks['Ticker'][:2]:
#     try:
#         # count += 1
#         # df = investpy.get_stock_historical_data(stock=ticker,country=country,from_date=f'{start}', to_date=f'{today}')
#         df = historical_stock_data(symbol, dailytype = 'line', start = one_years_ago_str, end =todaystr)
#         df1=financial_ratios(ticker=symbol,period='annual',ttm = True)
#         # df= df.rename(columns={"Close": "Adj Close"})
#         # print(f'Analyzing {count}.....{ticker}')
#         # print(df.info())  <== To see what you're getting
#         # df.to_csv(fr'data/{symbol}.csv')
#         # time.sleep(0.25)
#     except Exception as e:
#         st.write(e)
#         st.write(f'No data on {symbol}')
