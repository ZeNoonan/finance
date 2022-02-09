from contextlib import closing
import sched
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import seaborn as sns
import yahoo_fin.stock_info as si
from collections import OrderedDict
from dateutil.relativedelta import *
from datetime import date

st.set_page_config(layout="wide")
# https://www.nasdaq.com/market-activity/index/spx/historical
# https://fred.stlouisfed.org/categories/32255

data = pd.read_csv('C:/Users/Darragh/Documents/Python/aaron_brown/HistoricalData_1642969933291.csv')

data['Date']=pd.to_datetime(data['Date']).dt.normalize()
data['year']=data['Date'].dt.year
data['month']=data['Date'].dt.month
data['day']=data['Date'].dt.day
data=data.loc[:,['Date','year','Close/Last']]
data=data.sort_values(by='Date')
# st.write(data)


trading_days=data.groupby('year')['Close/Last'].count()
# st.write('trading days', trading_days)

data['starting_value']=1000000
data['units']=1000000/1316
data['portfolio_value']=data['units'] * data['Close/Last']

data['daily_move']=data['portfolio_value']-data['portfolio_value'].shift()
# data['daily_move']=data['portfolio_value']-data['shift']

data['daily_move_%']=data['daily_move'] / data['portfolio_value']
data['check_move_%'] = data['Close/Last'] / data['Close/Last'].shift()
# movement looks ok

data['port_movem']=data['daily_move_%']*1000000
# data['port_movem_shif']=data['port_movem'].shift(-1)
data['std_dev']=data['port_movem'].rolling(window=750,min_periods=1, center=False).std(ddof=1)
data['var_simple_estimate']=data['std_dev'] * 2.33

test_data=data.loc[:,['Date','year','var_simple_estimate','port_movem']]



# df_2=test_data.copy()
# df_2=df_2.iloc[:53,:].reset_index().drop('index',axis=1)
# # df_2['break?']=0
# # df_2['opening_var']=1000
# df_2['opening_var']=df_2['var_simple_estimate'].shift(-2)
# df_2['closing_var']=df_2['opening_var'] * 1
# df_2['break?']=np.where(df_2['port_movem'].abs()>df_2['opening_var'],1,0)
# # st.write('df2', df_2)
# # st.write('len',len(df_2))
# # df_2.iloc[[4], [df_2.columns.get_loc('break?')]]=1
# # df_2.iloc[[8], [df_2.columns.get_loc('break?')]]=1
# cols_to_move=['Date','year','var_simple_estimate','opening_var','port_movem','break?','closing_var']
# df_2 = df_2[ cols_to_move + [ col for col in df_2 if col not in cols_to_move ] ]
# data=df_2.copy()


# st.write('before looping',data)

simple_estimate=data['var_simple_estimate'].tolist()[2:]
port_movem=data['port_movem'].tolist()[2:]
opening_var=(data['var_simple_estimate']*1).tolist()[2:].copy()
opening_var=list(([10000]*(len(data[2:]))))
break_param=list(([0]*(len(data[2:]))))
# closing_var=simple_estimate.copy()
closing_var=list(([10000]*(len(data[2:]))))
# st.write(break_param)


raw_data=[]

for i,(simple_estimate, port_movem, opening_var, break_param,closing_var) in \
    enumerate(zip(simple_estimate[1:], port_movem[1:], opening_var[1:], break_param[1:],closing_var[1:])):
    opening_var=closing_var
    # st.write('i:',i,'opening var',opening_var)
    # st.write('i+1',opening_var[0])
    if break_param==0:
        # opening_var=closing_var
        closing_var=(opening_var*0.94)+(simple_estimate*.06)
        # opening_var=closing_var
        #  st.write('simp_est:',simple_estimate,'open:',opening_var,'close:',closing_var)
        raw_data.append((i,simple_estimate,port_movem,opening_var,break_param,closing_var))
    if break_param==1:
        closing_var=(opening_var*2)
        raw_data.append((i,simple_estimate,port_movem,opening_var,break_param,closing_var))
    
    opening_var=closing_var
    # st.write('open:',opening_var)
    # st.write('close:',closing_var)

          

df=pd.DataFrame(raw_data).rename(columns=({1:'simp_est',2:'port_move',3:'opening_var',4:'break',5:'closing_var'}))
st.write('table',df)

st.write('below is the data')
# st.write(data['var_simple_estimate'].tolist()[2:])
simple_estimate=data['var_simple_estimate'].tolist()[2:]
port_movem=data['port_movem'].tolist()[2:]
break_param=list(([0]*(len(data[2:]))))
# st.write(break_param)
# for _ in simple_estimate:
#     st.write('_',_)



def simple_function(simple_estimate,break_param,port_movem):
    opening_balance=simple_estimate[0]
    count = 1
    closing_balance=0
    for (estimate,break_param, movement) in zip(simple_estimate,break_param,port_movem):

        
        port_movem=movement*1
        break_param=break_param*1
        break_param=1 if abs(movement)>opening_balance else 0
        closing_balance=(estimate*0.06)+opening_balance*0.94 if break_param==0 else opening_balance*2

        yield OrderedDict([('estimate',estimate),('open_bal',opening_balance),('port_move',port_movem),('break',break_param),
        ('clos_bal',closing_balance),('Period',count)])
        count += 1
        opening_balance=closing_balance

st.write(pd.DataFrame(simple_function(simple_estimate,break_param=break_param,port_movem=port_movem)))

