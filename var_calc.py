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

st.write('before looping',data)

simple_estimate=data['var_simple_estimate'].tolist()[2:]
port_movem=data['port_movem'].tolist()[2:]
opening_var=(data['var_simple_estimate']*.5).tolist()[2:].copy()
opening_var=list(([10000]*(len(data[2:]))))
break_param=list(([0]*(len(data[2:]))))
# closing_var=simple_estimate.copy()
closing_var=list(([10000]*(len(data[2:]))))
# st.write(break_param)


raw_data=[]
# def run_function():

    # while True:
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
st.write(break_param)
# for _ in simple_estimate:
#     st.write('_',_)



def simple_function(simple_estimate,break_param,port_movem):
    opening_balance=simple_estimate[0]
    count = 1
    closing_balance=0
    # newx = []
    # mu = mean(x["X"])
    # sigma = std(x["X"])
    # while count <= len(simple_estimate):
    # while count > 0:
    # for (estimate) in (simple_estimate):
    # st.write('check port move', port_movem)
    for (estimate,break_param, movement) in zip(simple_estimate,break_param,port_movem):
        closing_balance=(estimate*0.1)+opening_balance*0.9
        port_movem=movement*1
        break_param=break_param*1
        yield OrderedDict([('estimate',estimate),('open_bal',opening_balance),('port_move',port_movem),('break',break_param),
        ('clos_bal',closing_balance),('Period',count)])
        count += 1
        opening_balance=closing_balance

st.write(pd.DataFrame(simple_function(simple_estimate,break_param=break_param,port_movem=port_movem)))


addl_principal=[100,200,300,400,500,600,700]

def amortize(principal, interest_rate, years, addl_principal=[0], annual_payments=12, start_date=date.today()):

    pmt = -round(np.pmt(interest_rate/annual_payments, years*annual_payments, principal), 2)
    # initialize the variables to keep track of the periods and running balances
    p = 1
    beg_balance = principal
    end_balance = principal

    while end_balance > 0:

        # for addl_principal in addl_principal:
            # Recalculate the interest based on the current balance
            interest = round(((interest_rate/annual_payments) * beg_balance), 2)

            # Determine payment based on whether or not this period will pay off the loan
            pmt = min(pmt, beg_balance + interest)
            principal = pmt - interest

            # Ensure additional payment gets adjusted if the loan is being paid off
            addl_principal = min(addl_principal, beg_balance - principal)
            end_balance = beg_balance - (principal + addl_principal)

            yield OrderedDict([('Month',start_date),
                            ('Period', p),
                            ('Begin Balance', beg_balance),
                            ('Payment', pmt),
                            ('Principal', principal),
                            ('Interest', interest),
                            ('Additional_Payment', addl_principal),
                            ('End Balance', end_balance)])

            # Increment the counter, balance and date
            p += 1
            start_date += relativedelta(months=1)
            beg_balance = end_balance

# schedule = pd.DataFrame(amortize(100000, .04, 30, addl_principal=addl_principal, start_date=date(2016, 1,1)))
# st.write(schedule)