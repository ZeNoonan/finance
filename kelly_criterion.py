from typing import OrderedDict
from altair.vegalite.v4.schema.core import Header
import pandas as pd
import numpy as np
import streamlit as st
# import yfinance as yf
from datetime import date
import random
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import os

# https://github.com/amolnaik/pynance
# https://github.com/razorhash/pyfmpcloud
# https://www.python-engineer.com/posts/stockprediction-app/


# https://twitter.com/10kdiver/status/1264622958468726785


# ALAD = 1
# x=random.choice([0.5,2])
# st.write(x)
# iterations=10
def comp(iterations):
    results=[]
    beg_balance = 1
    for _ in range(iterations):
        x=random.choice([0.5,2])
        end_balance = beg_balance * x
        yield OrderedDict([('beg_bal',beg_balance),('chance',x),('end_balance',end_balance)])
        beg_balance=end_balance
    # st.write('End Balance', end_balance)
        
data = pd.DataFrame(comp(iterations=20))

# https://wayback.archive-it.org/all/20090320125959/http://www.edwardothorp.com/sitebuildercontent/sitebuilderfiles/KellyCriterion2007.pdf
# page 20 sports betting


col1,col2=st.columns(2)
col3,col4=st.columns(2)
col5,col6=st.columns(2)
probaility_investment_goes_up_in_value=col1.number_input('probaility_investment_goes_up_in_value',value=0.55,step=.01)
# probaility_investment_goes_up_in_value=.55
probaility_investment_goes_down_in_value = 1-probaility_investment_goes_up_in_value
col2.write('probaility_investment_goes_down_in_value')
col2.write(format(probaility_investment_goes_down_in_value,".2f"))

fraction_lost_in_negative_outcome=col3.number_input('fraction_lost_in_negative_outcome',value=1.0,step=.05)
fraction_gained_in_positive_outcome = col4.number_input('fraction_gained_in_positive_outcome',value=.9,step=.05)

# per_cent_full_loss=(probaility_investment_goes_up_in_value) -\
# ((probaility_investment_goes_down_in_value)/fraction_gained_in_positive_outcome)
col5.write('divide above by bottom')
answer_left=probaility_investment_goes_up_in_value / fraction_lost_in_negative_outcome
col5.write(format(answer_left,".2f"))

col6.write('divide above by bottom')
answer_right=probaility_investment_goes_down_in_value/fraction_gained_in_positive_outcome
col6.write(format(answer_right,".2f"))


per_cent=(probaility_investment_goes_up_in_value / fraction_lost_in_negative_outcome) -\
((probaility_investment_goes_down_in_value)/fraction_gained_in_positive_outcome)
st.write("take away one from the other leaves the fraction to bet of your bankroll")
st.write("answer: % to bet is: ", format(per_cent,".2f"))

capital=st.number_input('capital',value=1000)
bet_per_stake = capital *per_cent

# st.write('bet_per_stake = capital * per_cent bet ', bet_per_stake)
# st.write(per_cent_full_loss)
# st.write(per_cent)
st.write('bet_per_stake = capital * per_cent bet ', format(bet_per_stake,".2f"))

st.write('what is the hold and how to calculate')


# if not os.path.exists('data'):
#     os.mkdir('data')

# for ticker in stocks['symbol']:
#     try:
#         count += 1
#         df = investpy.get_stock_historical_data(stock=ticker,country=country,from_date=f'{start}', to_date=f'{today}')
#         df= df.rename(columns={"Close": "Adj Close"})
#         # print(f'Analyzing {count}.....{ticker}')
#         # print(df.info())  <== To see what you're getting
#         df.to_csv(fr'data/{ticker}.csv')
#         time.sleep(0.25)