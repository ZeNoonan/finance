import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import seaborn as sns
from collections import OrderedDict
from dateutil.relativedelta import *
from datetime import date
import datetime as datetime

st.set_page_config(layout="wide")
# https://www.nasdaq.com/market-activity/index/spx/historical
# https://fred.stlouisfed.org/categories/32255



# data = pd.read_csv('C:/Users/Darragh/Documents/Python/aaron_brown/HistoricalData_1645994969204.csv')
# wilshire_data = pd.read_csv('C:/Users/Darragh/Documents/Python/aaron_brown/WILL5000INDFC.csv')

@st.cache
def read_data(x):
    return pd.read_csv(x)

data=read_data('C:/Users/Darragh/Documents/Python/aaron_brown/HistoricalData_1645994969204.csv').copy()
wilshire_data=read_data('C:/Users/Darragh/Documents/Python/aaron_brown/WILL5000INDFC.csv').copy()
# st.write('wilshire data after read', wilshire_data)

# st.write(test_data['WILL5000INDFC'].dtypes)
wilshire_data['WILL5000INDFC']=pd.to_numeric(wilshire_data['WILL5000INDFC'],errors='coerce')
wilshire_data=wilshire_data.rename(columns={'WILL5000INDFC':'Close/Last','DATE':'Date'})
wilshire_data=wilshire_data.dropna(subset=['Close/Last'])
# st.write('wilshire entire data',wilshire_data)

def data_date(data):
    data['Date']=pd.to_datetime(data['Date']).dt.normalize()
    data['year']=data['Date'].dt.year
    data['month']=data['Date'].dt.month
    data['day']=data['Date'].dt.day
    data=data.loc[:,['Date','year','Close/Last']]
    data=data.sort_values(by='Date')
    return data

data=data_date(data)
wilshire_data=data_date(wilshire_data)
wilshire_data=wilshire_data[(wilshire_data['Date']>pd.Timestamp(1980,1,1))]
# st.write('check date', wilshire_data)

trading_days=data.groupby('year')['Close/Last'].count()
wilshire_trading_days=wilshire_data.groupby('year')['Close/Last'].count()
# st.write('trading days', trading_days)

def data_process(data):
    data['daily_move_%']=((data['Close/Last'] / data['Close/Last'].shift())-1)
    # data['check_move_%'] = ((data['Close/Last'] / data['Close/Last'].shift())-1)
    # data['check_move_amt'] = (data['check_move_%'])*1000000
    # movement looks ok

    data['port_movem']=data['daily_move_%']*1000000
    data['std_dev']=data['port_movem'].rolling(window=750,min_periods=1, center=False).std()
    data['var_simple_estimate']=data['std_dev'] * 2.33

    simple_estimate=data['var_simple_estimate'].tolist()[2:]
    port_movem=data['port_movem'].tolist()[2:]
    date=data['Date'].tolist()[2:]
    return simple_estimate, port_movem, date




def simple_function(simple_estimate,port_movem,Date):
# def simple_function(simple_estimate,break_param,port_movem,Date):
    # sourcery skip: convert-to-enumerate, move-assign-in-block
    break_param=list(([0]*(len(simple_estimate[2:]))))

    opening_balance=simple_estimate[0]
    count = 1
    closing_balance=0
    for (estimate,break_param, movement,Date) in zip(simple_estimate,break_param,port_movem,Date):

        port_movem=movement*1
        break_param=break_param*1
        break_param=1 if abs(movement)>opening_balance else 0
        closing_balance=(estimate*0.06)+opening_balance*0.94 if break_param==0 else opening_balance*2

        yield OrderedDict([('estimate',estimate),('open_bal',opening_balance),('port_move',port_movem),('break',break_param),
        ('clos_bal',closing_balance),('Period',count),('Date',Date)])
        count += 1
        opening_balance=closing_balance

simple_estimate, port_movem, date=data_process(data)
df=pd.DataFrame(simple_function(simple_estimate,port_movem=port_movem,Date=date))
# st.write('df',df)

simple_estimate_1, port_movem_1, date_1=data_process(wilshire_data)
# st.write('check dates here',date_1)
# st.write('check estimate here',simple_estimate_1)
# st.write('check port move here',port_movem_1)
df_wilshire=pd.DataFrame(simple_function(simple_estimate_1,port_movem=port_movem_1,Date=date_1))
# st.write('df wilshire', df_wilshire)

def summary_stats(df):
    st.write('Total number of trading days:', df['estimate'].count())
    st.write('Total number of break days:', df['break'].sum())
    st.write('Percent of trading days that were a break:', df['break'].sum() / df['estimate'].count())

st.write('Summary Stats for S&P 500')
summary_stats(df)
st.write('Summary Stats for Wilshire')
summary_stats(df_wilshire)


def prepare_graph(df):
    df_graph_data=(df.loc[:,['Date','open_bal','port_move']])
    df_graph_data['open_bal_opp']=-df_graph_data['open_bal']
    df_graph_data=df_graph_data.melt(id_vars='Date',var_name='movement',value_name='value')
    return df_graph_data

df_graph_data=prepare_graph(df)
wilshire_graph_data=prepare_graph(df_wilshire)

# st.write(df_graph_data)
graph_2017 = df_graph_data[df_graph_data['Date'].dt.year==2017]
past_360_days = df_graph_data[df_graph_data['Date'] > datetime.datetime.now() - pd.to_timedelta("360day")]
past_720_days = df_graph_data[df_graph_data['Date'] > datetime.datetime.now() - pd.to_timedelta("720day")]
graph_2020 = df_graph_data[df_graph_data['Date'].dt.year==2020]
# df_graph_data=df_graph_data.melt(id_vars='open_bal',value_vars='Date')

def graph_altair(df_graph_data):
    return st.altair_chart(alt.Chart(df_graph_data).mark_line().encode(
    x=alt.X('Date',axis=alt.Axis(title='date',labelAngle=90)),
    y='value',
    color='movement',
    strokeDash='movement',
),use_container_width=True)

st.write('Below is Entire S&P History from 2012 to present')
(graph_altair(df_graph_data))

st.write('Below is Entire Wilshire History from 1980 to present')
(graph_altair(wilshire_graph_data))

# st.write('Below is 2017 Year')
# st.altair_chart(alt.Chart(graph_2017).mark_line().encode(
#     # x='yearmonth(Date):T',
#     x=alt.X('Date',axis=alt.Axis(title='date',labelAngle=90)),
#     # x=alt.X('year(Date):T',axis=alt.Axis(title='date',labelAngle=90)),
#     y='value',
#     color='movement',
#     strokeDash='movement',
# ),use_container_width=True)

st.write('Below is past 360 days for S&P')
(graph_altair(past_360_days))
# st.altair_chart(alt.Chart(past_360_days).mark_line().encode(
#     # x='yearmonth(Date):T',
#     x=alt.X('Date',axis=alt.Axis(title='date',labelAngle=90)),
#     # x=alt.X('year(Date):T',axis=alt.Axis(title='date',labelAngle=90)),
#     y='value',
#     color='movement',
#     strokeDash='movement',
# ),use_container_width=True)

wilshire_past_360_days = wilshire_graph_data[wilshire_graph_data['Date'] > datetime.datetime.now() - pd.to_timedelta("360day")]
(graph_altair(wilshire_past_360_days))

st.write('Below is Wilshire with Data Clamped')
st.altair_chart(alt.Chart(wilshire_graph_data).mark_line().encode(
    # x='yearmonth(Date):T',
    x=alt.X('Date',axis=alt.Axis(title='date',labelAngle=90)),
    # x=alt.X('year(Date):T',axis=alt.Axis(title='date',labelAngle=90)),
    y=alt.Y('value',scale=alt.Scale(
            domain=(-75000, 75000),clamp=True)),
    color='movement',
    strokeDash='movement',
),use_container_width=True)