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
        return pd.read_json(StringIO(data))


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

today = datetime.today()
todaystr = today.strftime("%Y-%m-%d")
ten_years_ago = datetime.today() - timedelta(days=10*365)
ten_years_ago_str = ten_years_ago.strftime("%Y-%m-%d")

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')

#https://github.com/JavierCastilloGuillen/Market_Screener/blob/master/screener_csv.py

st.title('Fundamentals')

st.sidebar.title("Setup")
st.sidebar.write("Please get your FMP API key here [link](https://financialmodelingprep.com/developer)")
api_key = st.sidebar.text_input('API Key', '', type="password")

try:
    if environ.get('fmp_key') is not None:
        set_apikey(os.environ['fmp_key'])
except:
    set_apikey(api_key)

symbol_search = st.sidebar.text_input('Symbol', 'AMZN')
#df_ticker = sts.ticker_search(match = symbol_search)

#scroll_list = list(df_ticker.name.values)
#scroll_list.append(symbol_search)

#selected = st.sidebar.selectbox('symbols found', scroll_list)




if st.sidebar.button("Start"):

    try:
        symbol = symbol_search
        #df_ticker.loc[df_ticker['name'] == selected,'symbol'][0]

        st.write('showing results for:', symbol)

        # get historical prices
        df_prices_ = historical_stock_data(symbol, dailytype = 'line', start = ten_years_ago_str, end =todaystr)
        df_prices = df_prices_.reset_index()
        st.write('df_prices',df_prices.head())
        # get financial ratios
        df_ratios = cv.financial_ratios(ticker=symbol,period='annual',ttm = False)
        st.write('df_ratios',df_ratios.head(5))
        # get performance metrics
        df_metrics = cv.key_metrics(ticker =symbol, period = 'annual')
        st.write('df_metrics',df_metrics.head())
        # get income statement
        df_income = cv.income_statement(ticker = symbol, period = 'annual', ftype = 'full')
        st.write('df_income',df_income.head())
        # get cashflow statement
        df_cashflow = cv.cash_flow_statement(ticker = symbol, period = 'annual', ftype = 'full')
        # get discounted cash_flow_statement
        df_dcf = cv.dcf(ticker = symbol, history = 'annual')

    except:
        st.write("Stock data unavailable!")
