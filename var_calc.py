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
data['var_simple_estimate']=data['std_dev'] * 2.33
data['var_c/f_update']=0
data['result_shift']=0

test_data=data.loc[:,['Date','year','var_simple_estimate','port_movem']]



df_2=test_data.copy()
df_2=df_2.iloc[:13,:].reset_index().drop('index',axis=1)
# df_2['break?']=0
# df_2['opening_var']=1000
df_2['opening_var']=df_2['var_simple_estimate'].shift(-2)
df_2['closing_var']=df_2['opening_var'] * 1
df_2['break?']=np.where(df_2['port_movem'].abs()>df_2['opening_var'],1,0)
# st.write('df2', df_2)
# st.write('len',len(df_2))
# df_2.iloc[[4], [df_2.columns.get_loc('break?')]]=1
# df_2.iloc[[8], [df_2.columns.get_loc('break?')]]=1
cols_to_move=['Date','year','var_simple_estimate','opening_var','port_movem','break?','closing_var']
df_2 = df_2[ cols_to_move + [ col for col in df_2 if col not in cols_to_move ] ]
data=df_2.copy()

for idx, row in df_2.iloc[1:].iterrows():
# https://stackoverflow.com/questions/38596056/how-to-change-the-starting-index-of-iterrows/38596799
# https://stackoverflow.com/questions/53792106/loop-through-dataframe-once-condition-is-met-start-loop-again-from-where-the-c
# https://stackoverflow.com/questions/23330654/update-a-dataframe-in-pandas-while-iterating-row-by-row/29262040?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

    if idx==len(df_2):
        # st.write('break:')
        # st.write('len df-1',len(df_2))
        break
    
    if row['break?']<0.9:
        # st.write('idx',idx)
        # st.write(np.sum(((df_2.iloc[[idx], [df_2.columns.get_loc('opening_var')]]) * .5).values.tolist()[0] +\
            #  ((df_2.iloc[[idx], [df_2.columns.get_loc('opening_var')]]) * .5).values.tolist()[0] ))
        # https://stackoverflow.com/questions/47917460/get-cell-value-from-a-pandas-dataframe-row/47917648
        # df_2.iloc[[idx], [df_2.columns.get_loc('closing_var')]] = (np.sum((df_2.iloc[[idx-1], [df_2.columns.get_loc('closing_var')]]).values.tolist()[0] * .94) \
        #     + ((df_2.iloc[[idx], [df_2.columns.get_loc('var_simple_estimate')]]).values.tolist()[0] * .06))
        df_2.iloc[[idx], [df_2.columns.get_loc('closing_var')]] = (((df_2.iloc[[idx-1], [df_2.columns.get_loc('closing_var')]])*.94))
        df_2.iloc[[idx], [df_2.columns.get_loc('opening_var')]] = (df_2.iloc[[idx-1], [df_2.columns.get_loc('closing_var')]])
    else:
        # st.write('idx:',idx, 'idx+1:',idx+1,'[break?]:',row['break?'])
        df_2.iloc[[idx], [df_2.columns.get_loc('closing_var')]] = df_2.iloc[[idx-1], [df_2.columns.get_loc('closing_var')]] * 2
        df_2.iloc[[idx], [df_2.columns.get_loc('opening_var')]] = (df_2.iloc[[idx-1], [df_2.columns.get_loc('closing_var')]])
        # st.write('oh oh break')

st.write('df2 after for loop',df_2)

st.write(data)
simple_estimate=data['var_simple_estimate'].tolist()[2:]
port_movem=data['port_movem'].tolist()[2:]
opening_var=simple_estimate.copy()
break_param=list(([0]*(len(data[2:]))))
closing_var=simple_estimate.copy()
# st.write(break_param)
# st.write(port_movem)

raw_data=[]
for i,(simple_estimate, port_movem, opening_var, break_param,closing_var) in \
     enumerate(zip(simple_estimate[1:], port_movem[1:], opening_var[1:], break_param[1:],closing_var[1:])):
    
    st.write('i:',i,'opening var',opening_var)
    opening_var=closing_var[i-1]
    st.write('i:',i,'opening var',opening_var)

    # if break_param==0:
    #     st.write('i:',i)
    # if i==0:
    #     break
    
        # st.write('yes')
    st.write(i,simple_estimate, port_movem, opening_var, break_param,closing_var)

# x=data.loc[0,['opening_var']]
# st.write(x)
# data['mask']=0
# data.loc[0,['mask']]=data.loc[0,['opening_var']].values.tolist()[0]
# st.write(data)



df = pd.DataFrame({'c1': [10, 11, 12], 'c2': [100, 110, 120]})
df = df.reset_index()  # make sure indexes pair with number of rows
# st.write(df)
# for index, row in df.iterrows():
    # st.write('row[C1]:',row['c1'],'row[C2]:', row['c2'])




# https://stackoverflow.com/questions/63687138/how-to-perform-a-rolling-summation-and-multiplication-in-pandas
# https://stackoverflow.com/questions/43710057/calculate-dataframe-values-recursively
# https://stackoverflow.com/questions/38008390/how-to-constuct-a-column-of-data-frame-recursively-with-pandas-python

df = pd.DataFrame([[100,100,0,0,0,0,0,0,0,0],[1.03, 1.02, 0.97, 1.02, 0.92, 1.08, 1.03 ,1.02, 1.03, 0.98],[0,0,0,0,0,0,0,0,0,0]]).T
df.index = ['2017-12-30', '2017-12-30', '2017-12-31','2018-01-01','2018-01-01',
            '2018-01-02','2018-01-02','2018-01-02','2018-01-03','2018-01-03']

# st.write('df',df)
# st.write('this df[1]', df[1]-1)
#initiate varaibles
res_col2 = []
res_col0 = []
s = 0 # same date result sum
# initiate values
mult = df.iloc[0,0]
idx0 = df.index[0]
# st.write('this is df before processing',mult)
# st.write('this is df before processing',df.index[0])
# loop with iteritems, not too bad with 3000 rows
for idx, val in (df[1]-1).iteritems(): #note the -1 is here already
    # st.write('idx:',idx)
    # st.write('val:',val)
    # update the mult and idx0 in case of not same date
    if idx != idx0:
        mult += s
        idx0 = idx
        s = 0
    # calculate the result
    r = mult*val
    s += r
    res_col2.append(r)
    res_col0.append(mult)

df[0] = res_col0
df[2] = res_col2

# st.write(df)