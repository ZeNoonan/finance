import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import seaborn as sns
import yahoo_fin.stock_info as si

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
# data['std_dev']=data['portfolio_value'].rolling(window=750,min_periods=1, center=False).std(ddof=1)
# data['std_dev_%']=data['std_dev'] / data['portfolio_value'] 
# data['std_dev_root']=np.sqrt(data['std_dev'])

# data['var']=data['std_dev_root'] * 2.33
data['shift']=data['portfolio_value'].shift()
# data['shift_price']=data['portfolio_value'].shift()

data['daily_move']=data['portfolio_value']-data['shift']
data['daily_move_%']=data['daily_move'] / data['portfolio_value']
data['port_movem']=data['daily_move_%']*1000000
# data['port_movem_shif']=data['port_movem'].shift(-1)
data['std_dev']=data['port_movem'].rolling(window=750,min_periods=1, center=False).std(ddof=1)
data['var']=data['std_dev'] * 2.33

# data['dummy_column'] = data['result']*data['var']

data['0.06 today'] = data['var'] * 0.06
data['var yesterday'] = data['var'].shift(1)
data['0.94 yesterday'] = data['var yesterday'] * 0.94
data['updated_var']=data['0.06 today'] + data['0.94 yesterday']
data['var_c/f']=data['updated_var'].shift()


data['result']=np.where(data['port_movem'].abs()>data['var_c/f'],1,0)
data['result_shift']=data['result'].shift()
data['other_res']=1-data['result_shift']
data['roll_result']=data['result'].cumsum()
data['break_param']=data['result_shift'].replace({1:2})
data['var_c/f_2']=data['var_c/f'].shift()
data['var_c/f_update'] = (data['var_c/f'] * data['other_res']) + (data['var_c/f_2'] * data['break_param'])

data=data.reset_index().drop(['index','starting_value','units','portfolio_value','daily_move','shift'],axis=1)

st.write(data)
st.write('on day 9 we had a var break we calculated 13065 as var the evening before/this morning')
st.write('for day 10 we need a var of double the previous day')
st.write('for day 11 we need 94 percent of previous var')
st.write('Total number of trading days:', data['Close/Last'].count())
st.write('Total number of break days:', data['result'].sum())
st.write('Percent of trading days that were a break:', data['result'].sum() / data['Close/Last'].count())