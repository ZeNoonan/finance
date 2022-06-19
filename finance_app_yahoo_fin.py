import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import seaborn as sns
# import yfinance as yf
from datetime import datetime
from datetime import timedelta
import yahoo_fin.stock_info as si


st.set_page_config(layout="wide")

# https://algotrading101.com/learn/yfinance-guide/
# seems to not recommend yfinance

# https://algotrading101.com/learn/yahoo-finance-api-guide/
# recommends this instead

# http://theautomatic.net/yahoo_fin-documentation/#methods



# dow_list = si.tickers_dow()
# dow_stats = {}
# for ticker in dow_list[:2]:
#     temp = si.get_stats_valuation(ticker)
#     temp = temp.iloc[:,:2]
#     temp.columns = ["Attribute", "Recent"]
#     dow_stats[ticker] = temp
# st.write(dow_stats)

# combined_stats = pd.concat(dow_stats)
# combined_stats = combined_stats.reset_index()
# # st.write(combined_stats)

# del combined_stats["level_1"]
# # update column names
# combined_stats.columns = ["Ticker", "Attribute", "Recent"]
# st.write(combined_stats.head())

# pe_ratios = combined_stats[combined_stats["Attribute"]=="Trailing P/E"].reset_index()
# st.write(pe_ratios)

stocks=pd.read_excel('C:/Users/Darragh/Documents/Python/finance_ratios/ticker_select.xlsx')

# st.write('quote table')
# user_dict=si.get_quote_table("aapl")
# st.write(user_dict)
# for k,v in user_dict.items():
#     st.write('',k, "-", v)

def stats(x):
    df=si.get_income_statement(ticker=x,yearly=False)
    df1=si.get_balance_sheet(ticker=x,yearly=False)
    # df=df.rename(columns={0:'Attribute',1:'Value'})
    return pd.concat([df,df1])
    
stats_df=stats("aapl")
st.write(stats_df)

def historical_price(x):
    df=si.get_data(x).reset_index().rename(columns={'index':'date'})
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df = df.loc[(df['date'] >= '2021-01-01')]
    return df.loc[:,['date','adjclose','ticker']]

df_prices=historical_price("aapl")
st.write(df_prices)

def get_stats_valuation_clean(x):
    df=si.get_stats_valuation(x)
    df1=si.get_stats(x)
    df=df.rename(columns={0:'Attribute',1:'Value'})
    return pd.concat([df,df1])

new_df=get_stats_valuation_clean("aapl")
st.write(new_df)




