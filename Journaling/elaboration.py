import Journaling.download_data as download
import Journaling.config_upload as conf
import pandas as pd
import datetime
import numpy as np
import statsmodels.api as sm
from scipy import stats
from matplotlib import pyplot as plt



pd.options.mode.chained_assignment = None

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', None)  # or 199

OUTPUT = '.\output\\'
JOURNAL = '.\output\\journal\\'
HISTORY = conf.history()

def go():
    df = pd.read_csv(JOURNAL + 'journal.csv')
    print(df.columns)

    # Convert al time into data that can i use after
    df['premarket_time_high'] = pd.to_datetime(df['premarket_time_high'], format='%H:%M:%S').dt.time
    df['premarket_time_low'] = pd.to_datetime(df['premarket_time_low'], format='%H:%M:%S').dt.time
    df['firsthour_high_time'] = pd.to_datetime(df['firsthour_high_time'], format='%H:%M:%S').dt.time
    df['firsthour_low_time'] = pd.to_datetime(df['firsthour_low_time'], format='%H:%M:%S').dt.time
    df['morning_high_time'] = pd.to_datetime(df['morning_high_time'], format='%H:%M:%S').dt.time
    df['morning_low_time'] = pd.to_datetime(df['morning_low_time'], format='%H:%M:%S').dt.time
    df['middle_high_time'] = pd.to_datetime(df['middle_high_time'], format='%H:%M:%S').dt.time
    df['middle_low_time'] = pd.to_datetime(df['middle_low_time'], format='%H:%M:%S').dt.time
    df['afternoon_high_time'] = pd.to_datetime(df['afternoon_high_time'], format='%H:%M:%S').dt.time
    df['afternoon_low_time'] = pd.to_datetime(df['afternoon_low_time'], format='%H:%M:%S').dt.time
    df['market_high_time'] = pd.to_datetime(df['market_high_time'], format='%H:%M:%S').dt.time
    df['market_low_time'] = pd.to_datetime(df['market_low_time'], format='%H:%M:%S').dt.time
    df['afterhour_high_time'] = pd.to_datetime(df['afterhour_high_time'], format='%H:%M:%S').dt.time
    df['afterhour_low_time'] = pd.to_datetime(df['afterhour_low_time'], format='%H:%M:%S').dt.time

    # add the calculate columns
    df['premarket_low_price'] = df['premarket_high']*(1+df['premarket_low']/100)
    df['gap'] = (df['Open_price'] - df['Prev_close'])/df['Prev_close']*100
    df['PMH_O'] = (df['premarket_high'] - df['Open_price'])/df['premarket_high']*100
    df['PMH_H'] = (df['market_high'] - df['premarket_high']) / df['premarket_high'] * 100
    df['OH'] = (df['market_high'] - df['Open_price'])/df['Open_price']*100
    df['OL'] = (df['market_low'] - df['Open_price'])/df['Open_price']*100
    df['GZ_H'] = (df['premarket_high'] - df['Prev_close']) * 0.886 + df['Prev_close']
    df['GZ_L'] = (df['premarket_high'] - df['Prev_close']) * 0.786 + df['Prev_close']

    red_close = df[df['Open_price'] > df['close_price']]
    green_close = df[df['Open_price'] <= df['close_price']]
    never_break_pm_high = df[df['premarket_high'] >= df['market_high'] ]
    break_pm_high = df[df['premarket_high'] < df['market_high'] ]
    break_pm_close_below_pm_high = break_pm_high[break_pm_high['close_price'] < break_pm_high['premarket_high']]
    break_pm_close_below_open = break_pm_high[break_pm_high['close_price'] < break_pm_high['Open_price']]
    break_pm_touch_pm_low = break_pm_high[break_pm_high['close_price'] <= break_pm_high['premarket_low_price']]

    #print(break_pm_high[{'Date', 'Float', 'market_low', 'premarket_low'}])

    fig, (ax1,ax2) = plt.subplots(2)

    resid_std = break_pm_close_below_pm_high['OH']
    ax1.hist(resid_std, bins=50)
    ax1.set_title('Histogram Extension above open price')

    resid_std = break_pm_close_below_pm_high['PMH_H']
    ax2.hist(resid_std, bins=50)
    ax2.set_title('Histogram Extension above premarket highs')
    plt.show()


    print('===========================================')
    print('STATISTIC OF DATA STOCK')
    print('===========================================')
    print('Number of stocks analyzed: {}'.format(df.shape[0]))
    print('Close green: {} - {:.2f}%'.format(green_close.shape[0],
                                             green_close.shape[0]/df.shape[0]*100))
    print('Close red: {} - {:.2f}%'.format(red_close.shape[0],
                                             red_close.shape[0]/df.shape[0]*100))

    print('===========================================')
    print('GAP & CRAP')
    print('===========================================')
    print('Never break the premarket highs: {} - {:.2f}%'.format(never_break_pm_high.shape[0],
                                            never_break_pm_high.shape[0]/df.shape[0]*100))


    print('===========================================')
    print('GAP & EXTENSION')
    print('===========================================')
    print('Break the premarket highs: {} - {:0.2f}%'.format(break_pm_high.shape[0],
                                            never_break_pm_high.shape[0] / df.shape[0] * 100))

    print('Break the premarket highs and close below premarket high: {} - {:0.2f}%'.format(break_pm_close_below_pm_high.shape[0],
                                            break_pm_close_below_pm_high.shape[0] / break_pm_high.shape[0] * 100))

    print('Average extension:')
    print('Extension above open price: {:.2f}% (dev standard +-{:.2f}%)'.format(
        break_pm_close_below_pm_high['OH'].mean(),
        break_pm_close_below_pm_high['OH'].std()
    ))
    print('Extension above premarket high: {:.2f}% (dev standard +-{:.2f}%)'.format(
        break_pm_close_below_pm_high['PMH_H'].mean(),
        break_pm_close_below_pm_high['PMH_H'].std()
    ))
    print('Hour high market:')
    hour_market_list(break_pm_close_below_pm_high, 'market_high_time')
    print('Hour low market:')
    hour_market_list(break_pm_close_below_pm_high, 'market_low_time')


    print('Break the premarket highs and close below open price: {} - {:0.2f}%'.format(
        break_pm_close_below_open.shape[0],
        break_pm_close_below_open.shape[0] / break_pm_high.shape[0] * 100))

    print('Break the premarket highs and close below premarket low: {} - {:0.2f}%'.format(
        break_pm_touch_pm_low.shape[0],
        break_pm_touch_pm_low.shape[0] / break_pm_high.shape[0] * 100))

    flaot_range(break_pm_close_below_pm_high)


def statistic_gap(df, str, tot):
    df['PMH_O'] = (df['Open_price'] - df['premarket_high']) / df['premarket_high'] * 100


    print(' ===========================================')
    print(' STATISTIC GAP ' + str )
    print(' Cases: {} - {:.2f}% on total'.format(df.shape[0], df.shape[0] / tot.shape[0] * 100))
    print(' Average PM High vs open price: {:.2f}% (dev standard: +/-{:.2f}%)'.format(df['PMH_O'].mean(), df['PMH_O'].std()))
    hour_premarket_list(df,'premarket_time_high')

def hour_premarket_list(df, value):
    tot = df[value].count()
    range_1 = df[value].loc[df[value] < datetime.time(4,30,0)].count()
    range_2 = df[value].loc[(df[value] >= datetime.time(4, 30, 0)) & (df[value] < datetime.time(5, 3, 0))].count()
    range_3 = df[value].loc[(df[value] >= datetime.time(5, 3, 0)) & (df[value] < datetime.time(6, 3, 0))].count()
    range_4 = df[value].loc[(df[value] >= datetime.time(6, 3, 0)) & (df[value] < datetime.time(7, 3, 0))].count()
    range_5 = df[value].loc[(df[value] >= datetime.time(7, 3, 0)) & (df[value] < datetime.time(8, 3, 0))].count()
    range_6 = df[value].loc[(df[value] >= datetime.time(8, 3, 0)) & (df[value] < datetime.time(9, 3, 0))].count()

    print('04:00 and 04:30 : {:.2f}%'.format(range_1/tot * 100))
    print('04:30 and 05:30 : {:.2f}%'.format(range_2 / tot * 100))
    print('05:30 and 06:30 : {:.2f}%'.format(range_3 / tot * 100))
    print('06:30 and 07:30 : {:.2f}%'.format(range_4 / tot * 100))
    print('07:30 and 08:30 : {:.2f}%'.format(range_5 / tot * 100))
    print('08:30 and 09:30 : {:.2f}%'.format(range_6 / tot * 100))


def hour_market_list(df, value):
    tot = df[value].count()
    range_1 = df[value].loc[(df[value] >= datetime.time(9, 30, 0)) & (df[value] < datetime.time(9, 35, 0))].count()
    range_2 = df[value].loc[(df[value] >= datetime.time(9, 35, 0)) & (df[value] < datetime.time(9, 45, 0))].count()
    range_3 = df[value].loc[(df[value] >= datetime.time(9, 45, 0)) & (df[value] < datetime.time(10, 0, 0))].count()
    range_4 = df[value].loc[(df[value] >= datetime.time(10, 0, 0)) & (df[value] < datetime.time(10, 30, 0))].count()
    range_5 = df[value].loc[(df[value] >= datetime.time(10, 30, 0)) & (df[value] < datetime.time(11, 30, 0))].count()
    range_6 = df[value].loc[(df[value] >= datetime.time(11, 30, 0)) & (df[value] < datetime.time(13, 30, 0))].count()
    range_7 = df[value].loc[(df[value] >= datetime.time(13, 30, 0)) & (df[value] < datetime.time(14, 30, 0))].count()
    range_8 = df[value].loc[(df[value] >= datetime.time(14, 30, 0)) & (df[value] < datetime.time(15, 30, 0))].count()
    range_9 = df[value].loc[(df[value] >= datetime.time(15, 30, 0)) & (df[value] < datetime.time(16, 00, 0))].count()

    print('09:30 and 09:35 : {:.2f}%'.format(range_1/tot * 100))
    print('09:35 and 09:45 : {:.2f}%'.format(range_2 / tot * 100))
    print('09:45 and 10:00 : {:.2f}%'.format(range_3 / tot * 100))
    print('10:00 and 10:30 : {:.2f}%'.format(range_4 / tot * 100))
    print('10:30 and 11:30 : {:.2f}%'.format(range_5 / tot * 100))
    print('11:30 and 13:30 : {:.2f}%'.format(range_6 / tot * 100))
    print('13:30 and 14:30 : {:.2f}%'.format(range_7 / tot * 100))
    print('14:30 and 15:30 : {:.2f}%'.format(range_8 / tot * 100))
    print('15:30 and 16:00 : {:.2f}%'.format(range_9 / tot * 100))
def time_in_range(start, end, current):
    """Returns whether current is in the range [start, end]"""
    return start <= current <= end

def flaot_range(df):
    float1 = df['Float'].loc[df['Float'] < 1].count()
    float2 = df['Float'].loc[df['Float'] < 3].count() - float1
    float3 = df['Float'].loc[(df['Float'] >= 3) & (df['Float'] < 5)].count()
    float4 = df['Float'].loc[(df['Float'] >= 5) & (df['Float'] < 10)].count()
    float5 = df['Float'].loc[(df['Float'] >= 10) & (df['Float'] < 50)].count()
    float6 = df['Float'].loc[(df['Float'] >= 50) & (df['Float'] < 100)].count()
    float7 = df['Float'].loc[df['Float'] > 100].count()
    print('Float statistic:')
    print('Float less 1M: {:.2f}%'.format(float1/df.shape[0] * 100))
    print('Float between 1M and 3M: {:.2f}%'.format(float2/df.shape[0] * 100))
    print('Float between 3M and 5M: {:.2f}%'.format(float3 / df.shape[0] * 100))
    print('Float between 5M and 10M: {:.2f}%'.format(float4 / df.shape[0] * 100))
    print('Float between 10M and 50M: {:.2f}%'.format(float5 / df.shape[0] * 100))
    print('Float between 50 and 100M: {:.2f}%'.format(float6 / df.shape[0] * 100))
    print('Float between above 100M: {:.2f}%'.format(float7 / df.shape[0] * 100))