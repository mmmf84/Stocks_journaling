import Journaling.config_upload as conf
import pandas as pd
from pathlib import Path
import yfinance as yf
import numpy as np


OUTPUT = '.\output\\'
JOURNAL = '.\output\\journal'
STOCK = conf.stock()
TIMEFRAME = conf.timeframe()
KEY = conf.api_key()
SAVE_DATA = conf.save_data()
HISTORY = conf.history()
URL_EXT = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=' + STOCK + '&interval='+ TIMEFRAME + '&slice=' + HISTORY + '&apikey=' + KEY

def downlaod_data_ext():
    '''' Download the data extended'''
    file = OUTPUT + STOCK + '.csv'
    # check if the file exists
    file = OUTPUT + STOCK + '_' + HISTORY + '.csv'
    path = Path(file)

    if path.is_file():
        print("File exist")
    else:
        df = pd.read_csv(URL_EXT, index_col='time')
        df.index = pd.to_datetime(df.index)
        print(df)
        df.to_csv(file)

def yfinance_data():
    ticker = yf.Ticker(STOCK)
    #print(ticker.info)
    if hasattr(ticker.info, 'sector'):
        sector = 'nan'
    else:
        sector = insert_data(ticker.info['sector'])
    if hasattr(ticker.info, 'country'):
        country = 'nan'
    else:
        country = insert_data(ticker.info['country'])
    if conf.employees() == 'no':
        employess = 'nan'
    else:
        employess = insert_data(ticker.info['fullTimeEmployees'])
    if conf.float() == 'no':
        float = 'nan'
    else:
        float = round(insert_data(ticker.info['floatShares']) / 1000000,2)
    if conf.io() == 'no':
        io = 'nan'
    else:
        io = round(insert_data(ticker.info['heldPercentInstitutions']) * 100,2)
    if conf.short_ratio() == 'no':
        short_ratio = 'nan'
    else:
        short_ratio = round(ticker.info['shortPercentOfFloat'] * 100,2)

    data = {'sector': sector,
            'country': country,
            'employess': employess,
            'float': float,
            'io': io,
            'short_ratio': short_ratio}
    df = pd.DataFrame(data,index=[0])
    return df

def insert_data(info):
    data = info
    return data

