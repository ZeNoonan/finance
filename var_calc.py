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

data = pd.read_csv('C:/Users/Darragh/Documents/Python/aaron_brown/HistoricalData_1645994969204.csv')

data['Date']=pd.to_datetime(data['Date']).dt.normalize()
data['year']=data['Date'].dt.year
data['month']=data['Date'].dt.month
data['day']=data['Date'].dt.day
data=data.loc[:,['Date','year','Close/Last']]
data=data.sort_values(by='Date')

trading_days=data.groupby('year')['Close/Last'].count()
# st.write('trading days', trading_days)

data['daily_move_%']=((data['Close/Last'] / data['Close/Last'].shift())-1)
# data['check_move_%'] = ((data['Close/Last'] / data['Close/Last'].shift())-1)
# data['check_move_amt'] = (data['check_move_%'])*1000000
# movement looks ok

data['port_movem']=data['daily_move_%']*1000000
# st.write(data)
data['std_dev']=data['port_movem'].rolling(window=750,min_periods=1, center=False).std()
data['var_simple_estimate']=data['std_dev'] * 2.33

simple_estimate=data['var_simple_estimate'].tolist()[2:]
port_movem=data['port_movem'].tolist()[2:]
date=data['Date'].tolist()[2:]
opening_var=(data['var_simple_estimate']*1).tolist()[2:].copy()
opening_var=list(([10000]*(len(data[2:]))))
break_param=list(([0]*(len(data[2:]))))
closing_var=list(([10000]*(len(data[2:]))))
simple_estimate=data['var_simple_estimate'].tolist()[2:]
port_movem=data['port_movem'].tolist()[2:]
break_param=list(([0]*(len(data[2:]))))

def simple_function(simple_estimate,break_param,port_movem,Date):
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

df=pd.DataFrame(simple_function(simple_estimate,break_param=break_param,port_movem=port_movem,Date=date))
st.write(df)

st.write('Total number of trading days:', df['estimate'].count())
st.write('Total number of break days:', df['break'].sum())
st.write('Percent of trading days that were a break:', df['break'].sum() / df['estimate'].count())

df_graph_data=(df.loc[:,['Date','open_bal','port_move']])
df_graph_data['open_bal_opp']=-df_graph_data['open_bal']

df_graph_data=df_graph_data.melt(id_vars='Date',var_name='movement',value_name='value')
# df_graph_data=df_graph_data.melt(id_vars='Date')

st.write(df_graph_data)
graph_2017 = df_graph_data[df_graph_data['Date'].dt.year==2017]
past_360_days = df_graph_data[df_graph_data['Date'] > datetime.datetime.now() - pd.to_timedelta("360day")]
past_720_days = df_graph_data[df_graph_data['Date'] > datetime.datetime.now() - pd.to_timedelta("720day")]
graph_2020 = df_graph_data[df_graph_data['Date'].dt.year==2020]
# df_graph_data=df_graph_data.melt(id_vars='open_bal',value_vars='Date')

st.altair_chart(alt.Chart(df_graph_data).mark_line().encode(
    # x='yearmonth(Date):T',
    x=alt.X('Date',axis=alt.Axis(title='date',labelAngle=90)),
    # x=alt.X('year(Date):T',axis=alt.Axis(title='date',labelAngle=90)),
    y='value',
    color='movement',
    strokeDash='movement',
),use_container_width=True)

st.altair_chart(alt.Chart(graph_2017).mark_line().encode(
    # x='yearmonth(Date):T',
    x=alt.X('Date',axis=alt.Axis(title='date',labelAngle=90)),
    # x=alt.X('year(Date):T',axis=alt.Axis(title='date',labelAngle=90)),
    y='value',
    color='movement',
    strokeDash='movement',
),use_container_width=True)

st.altair_chart(alt.Chart(past_360_days).mark_line().encode(
    # x='yearmonth(Date):T',
    x=alt.X('Date',axis=alt.Axis(title='date',labelAngle=90)),
    # x=alt.X('year(Date):T',axis=alt.Axis(title='date',labelAngle=90)),
    y='value',
    color='movement',
    strokeDash='movement',
),use_container_width=True)

st.altair_chart(alt.Chart(graph_2020).mark_line().encode(
    # x='yearmonth(Date):T',
    x=alt.X('Date',axis=alt.Axis(title='date',labelAngle=90)),
    # x=alt.X('year(Date):T',axis=alt.Axis(title='date',labelAngle=90)),
    y='value',
    color='movement',
    strokeDash='movement',
),use_container_width=True)