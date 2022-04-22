import configparser
import datetime

config = configparser.ConfigParser()
config.read('.\config\config.ini')

def analisys():
    return config['SYSTEM']['analisys'].lower() == 'true'

def stock():
    '''' Return the stock name'''
    return config['ANALISYS']['stock'].upper()

def timeframe():
    '''' Return the timeframe that want download data'''
    return config['ALPHAVANTAGE']['timeframe']

def history():
    return config['ALPHAVANTAGE']['history']

def api_key():
    '''' apikey'''
    return config['ALPHAVANTAGE']['apikey'].upper()

def save_data():
    '''' Return if the want save download data'''
    return config['ANALISYS']['savefile'].lower() == 'true'

def stock_date():
    return config['ANALISYS']['date']

def open_time():
    return config['ALPHAVANTAGE']['open_time']

def close_time():
    return config['ALPHAVANTAGE']['close_time']

def employees():
    return config['FORCE']['employees']

def io():
    return config['FORCE']['io']

def short_ratio():
    return config['FORCE']['short_ratio']

def float():
    return config['FORCE']['float']

def prev_day_default():
    return int(config['FORCE']['prev_day'])
