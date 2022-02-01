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
# data['dummy_column'] = data['result']*data['var']
def calc(data):
    data['0.06 today'] = data['var_simple_estimate'] * 0.06
    data['var_simple_estimate_yesterday'] = data['var_simple_estimate'].shift(1)
    data['0.94 yesterday'] = data['var_simple_estimate_yesterday'] * 0.94
    data['updated_var']=data['0.06 today'] + data['0.94 yesterday']
    data['var_c/f']=data['updated_var'].shift()


    data['result']=np.where(data['port_movem'].abs()>data['var_c/f'],1,0)
    data['result_shift']=data['result'].shift()
    data['other_res']=1-data['result_shift']
    # data['roll_result']=data['result'].cumsum()
    data['break_param']=data['result_shift'].replace({1:2})
    data['var_c/f_2']=data['var_c/f'].shift()
    data['var_c/f_update'] = (data['var_c/f'] * data['other_res']) + (data['var_c/f_2'] * data['break_param'])
    return data

# data=calc(data)

# data=data.reset_index().drop(['index','starting_value','units','portfolio_value','daily_move','shift'],axis=1)



# st.write(data)
# st.write('on day 9 we had a var break we calculated 13065 as var the evening before/this morning')
# st.write('for day 10 we need a var of double the previous day')
# st.write('for day 11 we need 94 percent of previous var')
# st.write('Total number of trading days:', data['Close/Last'].count())
# st.write('Total number of break days:', data['result'].sum())
# st.write('Percent of trading days that were a break:', data['result'].sum() / data['Close/Last'].count())

# def amortize(principal, interest_rate, years, addl_principal=0, annual_payments=12, start_date=date.today()):

#     pmt = -round(np.pmt(interest_rate/annual_payments, years*annual_payments, principal), 2)
#     # initialize the variables to keep track of the periods and running balances
#     p = 1
#     beg_balance = principal
#     end_balance = principal

#     while end_balance > 0:

#         # Recalculate the interest based on the current balance
#         interest = round(((interest_rate/annual_payments) * beg_balance), 2)

#         # Determine payment based on whether or not this period will pay off the loan
#         pmt = min(pmt, beg_balance + interest)
#         principal = pmt - interest

#         # Ensure additional payment gets adjusted if the loan is being paid off
#         addl_principal = min(addl_principal, beg_balance - principal)
#         end_balance = beg_balance - (principal + addl_principal)

#         yield OrderedDict([('Month',start_date),
#                            ('Period', p),
#                            ('Begin Balance', beg_balance),
#                            ('Payment', pmt),
#                            ('Principal', principal),
#                            ('Interest', interest),
#                            ('Additional_Payment', addl_principal),
#                            ('End Balance', end_balance)])

#         # Increment the counter, balance and date
#         p += 1
#         start_date += relativedelta(months=1)
#         beg_balance = end_balance

# # schedule = pd.DataFrame(amortize(700000, .04, 30, addl_principal=200, start_date=date(2016, 1,1)))
# # st.write(schedule.tail())

# # st.write(test_data)



# def calc_test(data):
#     data=data.iloc[2:,:]
#     data['0.06 today'] = data['var_simple_estimate'] * 0.06
#     data['0.94 yesterday'] = data['var_simple_estimate'].shift() * 0.94
#     # data['break?']=0
#     # data['0.94 yesterday']=0
#     data['0.94 calc']=0
#     data['var']=data['0.06 today'] + data['0.94 yesterday']
#     data['var_yesterday']=data['var'].shift()
    
#     data['break?']=np.where(data['port_movem'].abs()>data['var_yesterday'],1,0)
#     data['var']=np.where(data['break?']==1,(data['var_yesterday']*2),(data['0.06 today']+data['0.94 yesterday']))
#     # data['break?']=np.where(data['port_movem'].abs()>data['var'],1,0)
    
#     data['var_yesterday']=data['var'].shift()
#     data['0.94 yesterday'] =data['var_yesterday'] * .94 
#     # st.write('this is var after')
#     # data['var']=data['0.06 today'] + data['0.94 calc']
    
#     # data['0.06 today'] = data['var_simple_estimate'] * 0.06
#     # data['0.94 calc']=np.where(data['break?']==1,data['var_yesterday']*2,data['var_yesterday']*.94)    
#     # data['var']=data['0.06 today'] + data['0.94 calc']
    
#     # data['other_res']=1-data['result_shift']
#     return data

# # test_data=calc_test(test_data)
# # st.write(test_data['break?']==1)
# # st.write('zero test')
# # st.write(test_data)

# def calc_test_1(data):
#     data=data.iloc[2:,:]
#     data['0.06 today'] = data['var_simple_estimate'] * 0.06
#     data['var']=0
#     data['0.94 yesterday'] = data['var_simple_estimate'].shift() * 0.94
#     data['var']=data['0.06 today'] + data['0.94 yesterday']
    
#     data['break?']=np.where(data['port_movem'].abs()>data['var'].shift(),1,0)
#     data['var']=np.where(data['break?']==1,((data['var'].shift())*2),(data['var']))
    
#     return data

# # st.write('first test')
# # st.write(calc_test_1(test_data))

# def calc_test_2(data):
#     data=data.iloc[2:,:]
#     data['break?']=0
#     data['var']=data['port_movem'].abs()+1
#     data['var']=data['var']
#     # First thing, is there a break
#     data['break?']=np.where(data['port_movem'].abs()>data['var'].shift(),1,0)
#     data['var'] = (data['var_simple_estimate'] * 0.06) + data['var_simple_estimate'].shift() * 0.94
#     data['var']=np.where(data['break?']==1,((data['var'].shift())*2),(data['var']))
    
#     return data

# st.write('second test')
# st.write(calc_test_2(test_data))


# df_1=test_data.copy()
# # df_1=df_1.iloc[3:13,:].copy().reset_index().drop('index', axis=1)
# df_1=df_1.iloc[:13,:]
# # df_1['yesterday_var_simple_estimate']=df_1['var_simple_estimate'].shift()
# df_1['break?']=0
# df_1['opening_var']=15000
# # st.write('test_0',df_1)
# df_1=df_1.iloc[2:,:].reset_index().drop('index',axis=1)
# # st.write(df_1.loc[0,['var']])
# # st.write(df_1.loc[0,['var_simple_estimate']])
# # df_1.loc[0,['var']]=df_1.loc[0,['var_simple_estimate']]
# df_1['closing_var']=15000

# st.write('test_1',df_1)
# df_1['var'] = (df_1['var_simple_estimate'] * .06) + (df_1['var'].shift()*.94)
# st.write(df_1.head())

# delete first two rows as need to calculate first
# st.write(df_1.iloc[:2,:])
# # st.write(df_1.iloc[2:,:])
# df_1['break?']=np.where(df_1['port_movem'].abs()>df_1['var'].shift(),1,0)
# df_1['var']=np.where((df_1['break?'].shift())==1,((df_1['var'].shift())*2),(df_1['var_simple_estimate'] * .06) + (df_1['var'].shift()*.94))
# # df_1['var']=np.where((df_1['break?'].shift())==0,
# # df_1['var']=df_1['port_movem'].abs()+1

# https://stackoverflow.com/questions/23330654/update-a-dataframe-in-pandas-while-iterating-row-by-row/29262040?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
# for i in range(1, len(df) + 1):
#     j = df.columns.get_loc('ifor')
#     if <something>:
#         df.iat[i - 1, j] = x
#     else:
#         df.iat[i - 1, j] = y

df_2=test_data.copy()
df_2=df_2.iloc[:13,:].reset_index().drop('index',axis=1)
df_2['break?']=0
df_2['opening_var']=1000
df_2['closing_var']=df_2['opening_var'] * .5
st.write('len',len(df_2))
df_2.iloc[[6], [df_2.columns.get_loc('break?')]]=1
st.write('df2',df_2)
# for i in range(1, (len(df_2))):
#     if (df_2.loc[0,['break?']]==0).any():
#         df_2.iloc[[i], [df_2.columns.get_loc('closing_var')]] = (df_2.iloc[[i-1], [df_2.columns.get_loc('closing_var')]]) * .5
#         df_2.iloc[[i], [df_2.columns.get_loc('opening_var')]] = (df_2.iloc[[i-1], [df_2.columns.get_loc('closing_var')]])
#     else:
#         st.write('oh oh break')

# for i in range(1, (len(df_2))):
for idx, row in df_2.iterrows():
    if idx==len(df_2)-1:
        break
    # if (df_2.loc[~['break?']]==1):
    if row['break?']<1:
        df_2.iloc[[idx+1], [df_2.columns.get_loc('closing_var')]] = (df_2.iloc[[idx], [df_2.columns.get_loc('closing_var')]]) * .5
        df_2.iloc[[idx+1], [df_2.columns.get_loc('opening_var')]] = (df_2.iloc[[idx], [df_2.columns.get_loc('closing_var')]])
    # df_2['opening_var'] = df_2['closing_var']
    else:
        st.write('oh oh break')



st.write('df2 after for loop',df_2)




# raw_data=[]
# for index, row in df_1.iterrows():
#     if row['break?'] == 0:
#         row['closing_var'] = (row['var_simple_estimate']*0.06)+(row['opening_var']*0.94)
#         row['opening_var'] = row['closing_var']
#         st.write(row)
#         # raw_data.append(row)# st.write(row['var'])
#     # pass
    # st.write('var_simple',row['var_simple_estimate'])
#     # st.write('port_movem',row['port_movem'])
# st.write('df1')
# st.write(pd.concat([raw_data]))

# for index, row in df_1.iterrows():



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