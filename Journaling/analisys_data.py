import Journaling.download_data as download
import Journaling.config_upload as conf
import pandas as pd
import datetime
from datetime import timedelta
import datetime

STOCK = conf.stock()
DATE = conf.stock_date()
OUTPUT = '.\output\\'
JOURNAL = '.\output\\journal\\'
HISTORY = conf.history()

def go():
    ''''Function to start the program of journaling'''
    # Ricordati di decommentare download data
    download.downlaod_data_ext()
    info = download.yfinance_data()
    extract_data(info)

def extract_data(info):
    print('===================================')
    print('STOCK INFORMATION')
    print('===================================')
    print('Stock: {}'.format(STOCK))
    print('Date: {}'.format(DATE))
    print('Sector: {}'.format(info['sector'][0]))
    print('Country: {}'.format(info['country'][0]))
    print('Employess: {}'.format(info['employess'][0]))
    print('Float: {}M'.format(info['float'][0]))
    print('IO: {}%'.format(info['io'][0]))
    print('Short ratio: {}%'.format(info['short_ratio'][0]))

    df = upload_data()
    df['middle'] = (df['high'] - df['low'])/2 + df['low']
    df['vol_tick'] = df['volume'] / (df['high'] - df['low'])
    #print(df.loc[df['volume']>3000000].sort_values(by='vol_tick', ascending=False).head(50))
    prev = prev_day() + ' ' + conf.close_time()
    prev_day_close = df['close'].loc[prev]
    # Add col with var vs prev day close
    df['var_prev_close'] = (df['close'] - prev_day_close) / prev_day_close * 100
    # round the data
    df = df.round({'open':2, 'high':2, 'low':2, 'close':2, 'volume': 0, 'var_prev_close': 2})

    # Divide the data into the session of trading hours
    premarket_data = market_hours(df, ' 04:00:00', ' 09:30:00')
    market_data = market_hours(df, ' 09:30:00', ' 16:00:00')
    first_hour = market_hours(df, ' 09:30:00', ' 10:30:00')
    morning_hour = market_hours(df, ' 09:30:00', ' 12:00:00')
    middle_hour = market_hours(df, ' 12:00:00', ' 14:00:00')
    afternoon_hour = market_hours(df, ' 14:00:00', ' 16:00:00')
    post_data = market_hours(df, ' 16:00:00', ' 20:00:00')

    # Extract cumulative volume for each session
    vol_pm = cum_vol(premarket_data)
    vol_mkt = cum_vol(market_data)
    vol_morning = cum_vol(morning_hour)
    vol_middle = cum_vol(middle_hour)
    vol_afternoon = cum_vol(afternoon_hour)
    vol_fh = cum_vol(first_hour)
    vol_ah = cum_vol(post_data)

    vol_tot = vol_pm + vol_mkt + vol_ah


    print('Volume day : %.2fM' % vol_tot)

    # PREMARKET EXTRACT INFO
    high_premarket, time_pm_high, vol_pm_high = high_statistic(premarket_data)
    premarket_until_high = market_hours(df, ' 04:00:00', ' ' + time_pm_high)
    vol_pm_high_cum = cum_vol(premarket_until_high)
    premarket_after_high = market_hours(df, ' ' + time_pm_high, ' 09:30:00')
    premarket_after_high['var_high_pm'] = round((premarket_after_high['low'] - high_premarket) / high_premarket * 100,2)
    low_premarket_after_high = premarket_after_high['var_high_pm'].min()
    time_pm_low_after_high = premarket_after_high.loc[premarket_after_high['var_high_pm'] == low_premarket_after_high].index.strftime("%H:%M")[0] + ':00'

    golden_zone_low, golden_zone_high = golden_zone_level(high_premarket, prev_day_close)
    print('===================================')
    print('PREMARKET INFORMATION')
    print('===================================')
    print('High: {:0.2f}({:0.2f}% from open) at {} with volume {:.2f}M and cumulative vol {:0.2f}M'.format(high_premarket,((high_premarket - prev_day_close) / prev_day_close * 100), time_pm_high, vol_pm_high,vol_pm_high_cum))
    print('Low after high: {:.2f}({}%) at {}'.format(premarket_after_high['low'].min(),low_premarket_after_high, time_pm_low_after_high))
    print('Volume premarket : %.2fM' % (vol_pm))
    print('Golden zone high: {:.2f} (var prev day close : {:.2f}%)'.format(golden_zone_high, ((golden_zone_high - prev_day_close) / prev_day_close * 100)))
    print('Golden zone low {:.2f} (var prev day close : {:.2f}%)'.format(golden_zone_low, ((golden_zone_low - prev_day_close) / prev_day_close * 100)))

    # MARKET EXTRACT INFO
    open_time = DATE + ' ' + conf.open_time()
    open_level = df['open'].loc[open_time]
    highpm_open_var = (open_level - high_premarket) / high_premarket * 100

    # FIRST HOUR STATISTIC
    # high of first hour statistic
    high_firsthour, time_firsthour_high, vol_fh_high, vol_cum_fh_high, low_firsthour, time_firsthour_low, vol_fh_low, vol_cum_fh_low = statistic_hour(first_hour, df, open_level, 'FIRST')

    # MORNING HOUR STATISTIC
    high_morning, time_morning_high, vol_morning_high, vol_cum_morning_high, low_morning, time_morning_low, vol_morning_low, vol_cum_morning_low = statistic_hour(morning_hour, df, open_level, 'MORNING')

    # MIDDLE HOUR STATISTIC
    high_middle, time_middle_high, vol_middle_high, vol_cum_middle_high, low_middle, time_middle_low, vol_middle_low, vol_cum_middle_low = statistic_hour(middle_hour, df, open_level, 'MIDDLE')

    # AFTERNOON HOUR STATISTIC
    high_afternoon, time_afternoon_high, vol_afternoon_high, vol_cum_afternoon_high, low_afternoon, time_afternoon_low, vol_afternoon_low, vol_cum_afternoon_low = statistic_hour(
        afternoon_hour, df, open_level, 'AFTERNOON')

    # MARKET STATISTIC
    gap = (open_level - prev_day_close) / prev_day_close * 100
    high_market, time_high_market, vol_market_high, vol_cum_market_high, low_market, time_market_low, vol_candle_low_market, vol_cum_market_low = statistic_hour(market_data, df, open_level, 'MARKET')
    close_time = DATE + ' ' + conf.close_time()
    close_price = df['close'].loc[close_time]

    print('Gap: {:.2f}% - open price: {:.2f}'.format(gap, open_level))
    print('High premarket open price var: {}%'.format(round(highpm_open_var, 2)))

    # AFTER HOUR STATISTIC
    afterhour_high, afterhour_time_high, afterhour_vol_high, afterhour_vol_cum_high, afterhour_low, afterhour_time_low, afterhour_vol_low, afterhour_vol_cum_low = statistic_hour(post_data, df, open_level, 'AFTER')
    data = {'Date': DATE,
            'Stock': STOCK,
            'Sector': info['sector'][0],
            'Country': info['country'][0],
            'Employess': info['employess'][0],
            'Float': info['float'][0],
            'Io': info['io'][0],
            'Short_ratio': info['short_ratio'][0],
            'Prev_close': prev_day_close,
            'premarket_high': high_premarket,
            'premarket_time_high': time_pm_high,
            'premarket_vol_high': vol_pm_high,
            'premarket_vol_cum_high': vol_pm_high_cum,
            'premarket_low': low_premarket_after_high,
            'premarket_time_low': time_pm_low_after_high,
            'premarket_volume': vol_pm,
            'Open_price': open_level,
            'firsthour_high': high_firsthour,
            'firsthour_high_time': time_firsthour_high,
            'firsthour_vol_high' : vol_fh_high,
            'firsthour_vol_cum_high': vol_cum_fh_high,
            'firsthour_low': low_firsthour,
            'firsthour_low_time': time_firsthour_low,
            'firsthour_vol_low': vol_fh_low,
            'firsthour_vol_cum_low': vol_cum_fh_low,
            'firsthour_volume': vol_fh,
            'morning_high': high_morning,
            'morning_high_time': time_morning_high,
            'morning_vol_high': vol_morning_high,
            'morning_vol_cum_high': vol_cum_morning_high,
            'morning_low': low_morning,
            'morning_low_time': time_morning_low,
            'morning_vol_low': vol_morning_low,
            'morning_vol_cum_low': vol_cum_morning_low,
            'morning_volume': vol_morning,
            'middle_high': high_middle,
            'middle_high_time': time_middle_high,
            'middle_vol_high': vol_middle_high,
            'middle_vol_cum_high': vol_cum_middle_high,
            'middle_low': low_middle,
            'middle_low_time': time_middle_low,
            'middle_vol_low': vol_middle_low,
            'middle_vol_cum_low': vol_cum_middle_low,
            'middle_volume': vol_middle,
            'afternoon_high': high_afternoon,
            'afternoon_high_time': time_afternoon_high,
            'afternoon_vol_high': vol_afternoon_high,
            'afternoon_vol_cum_high': vol_cum_afternoon_high,
            'afternoon_low': low_afternoon,
            'afternoon_low_time': time_afternoon_low,
            'afternoon_vol_low': vol_afternoon_low,
            'afternoon_vol_cum_low': vol_cum_afternoon_low,
            'afternoon_volume': vol_afternoon,
            'market_high': high_market,
            'market_high_time': time_high_market,
            'market_vol_high': vol_market_high,
            'market_vol_cum_high': vol_cum_market_high,
            'market_low': low_market,
            'market_low_time': time_market_low,
            'market_vol_low': vol_candle_low_market,
            'market_vol_cum_low': vol_cum_market_low,
            'market_volume': vol_mkt,
            'close_price': close_price,
            'afterhour_high': afterhour_high,
            'afterhour_high_time': afterhour_time_high,
            'afterhour_vol_high': afterhour_vol_high,
            'afterhour_vol_cum_high': afterhour_vol_cum_high,
            'afterhour_low': afterhour_low,
            'afterhour_low_time': afterhour_time_low,
            'afterhour_vol_low': afterhour_vol_low,
            'afterhour_vol_cum_low': afterhour_vol_cum_low,
            'afterhour_volume': vol_ah,
            }

    dt = pd.DataFrame(data, index=['Date'])
    with open(JOURNAL + 'journal.csv', 'a') as f:
        (dt).to_csv(f, header=False, index=False)

def upload_data():
    file = OUTPUT + STOCK + '_' + HISTORY + '.csv'
    df = pd.read_csv(file,index_col='time', parse_dates=True)
    df = df.sort_index(ascending=True)
    return df

def prev_day():
    day = datetime.datetime.strptime(DATE, '%Y-%m-%d')
    prev = day - timedelta(days=conf.prev_day_default()) #default 1
    if prev.weekday() == 6:
        prev = day - timedelta(days=3) #default 3
    print(prev.weekday())
    prev_day = prev.strftime('%Y-%m-%d')
    return prev_day

def market_hours(df, time1, time2):
    ''''Divide the hours trading - premarket, firsthours, market, after hour ecc'''
    hour_start = DATE + time1
    hour_end = DATE + time2
    return df.loc[hour_start : hour_end]

def cum_vol(df):
    ''''Calculate the cumulative volume in M'''
    return round(df['volume'].sum()/1000000,2)

def golden_zone_level(high_pm, prev_close):
    ''''returns the golden zone levels. low and high'''
    golden_zone_low = (high_pm - prev_close) * 0.786 + prev_close
    golden_zone_high = (high_pm - prev_close) * 0.886 + prev_close
    return golden_zone_low, golden_zone_high

def high_statistic(df):
    high_ = df['high'].max()
    time_ = df.loc[df['high'] == high_].index.strftime("%H:%M")[0] + ':00'
    vol_ = df['volume'].loc[df['high'] == high_].values[0] / 1000000
    return high_, time_, vol_

def low_statistic(df):
    low_ = df['low'].min()
    time_ = df.loc[df['low'] == low_].index.strftime("%H:%M")[0] + ':00'
    vol_ = df['volume'].loc[df['low'] == low_].values[0] / 1000000
    return low_, time_, vol_

def statistic_hour(df,dt,open_level, hour_title):
    high_hour, time_high, vol_high = high_statistic(df)
    high_hour_open = (high_hour - open_level) / open_level * 100

    low_hour, time_low, vol_low = low_statistic(df)
    low_hour_open = (low_hour - open_level) / open_level * 100

    volume_candle_hour = df['volume'].max()
    time_hour_volume = df.loc[df['volume'] == volume_candle_hour].index.strftime("%H:%M")[
                             0] + ':00'

    vol_tot = cum_vol(df)

    data_until_high = market_hours(dt, ' 04:00:00', ' ' + time_high)
    vol_high_cum = cum_vol(data_until_high)

    data_until_low = market_hours(dt, ' 04:00:00', ' ' + time_low)
    vol_low_cum = cum_vol(data_until_low)

    print('===================================')
    print('{} HOUR INFORMATION'.format(hour_title.upper()))
    print('===================================')
    print('High: {:.2f}({:0.2f}%) at {} with volume {:.2f}M and volume cum {:.2f}M'.format(high_hour, high_hour_open, time_high,
                                                                    vol_high, vol_high_cum))
    print('Low: {:.2f}({:0.2f}%) at {} with volume {:.2f}M and volume cum {:.2f}M'.format(low_hour, low_hour_open, time_low,
                                                                   vol_low, vol_low_cum))
    print('Volume: {:.2f}M at {}'.format(volume_candle_hour / 1000000, time_hour_volume))
    print('Volume {} hour : {:.2f}M'.format(hour_title.lower(),vol_tot))
    return high_hour, time_high, vol_high,vol_high_cum, low_hour, time_low, vol_low,vol_low_cum