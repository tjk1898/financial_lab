import akshare as ak
import pandas as pd
import datetime as dt
import talib as tl
import matplotlib.pyplot as plt
import shelve
import os
from utils.drawer import get_line
from pyecharts import options as opts


def get_price(security, str_start_date=None, str_end_date=None, period=1800):
    time_pattern = '%Y%m%d'
    if str_start_date is None:
        if str_end_date is None:
            end_date = dt.datetime.today()
        else:
            end_date = dt.datetime.strptime(str_end_date, time_pattern)
        start_date = end_date - dt.timedelta(days=period)
        str_start_date = start_date.strftime(time_pattern)
    price = ak.stock_zh_a_hist(symbol=security, period="daily", start_date=str_start_date, end_date=str_end_date,
                               adjust="qfq")
    price.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'turnover', 'amp_rate', 'quote_rate',
                     'quote_num', 'turnover_rate']
    return price


def read_df(code):
    file = ''
    path = os.path.dirname(os.path.abspath('./'))
    path = os.path.join(path, '../AKshareTest/continue_rise/data/')
    filenames = os.listdir(path)

    for i in filenames:
        if code in i:
            file = os.path.join(path, i)
            print(file)
            df = pd.read_csv(file)
            if 'Unnamed: 0' in df.columns:
                del df['Unnamed: 0']
            if 'amount' in df.columns:
                df.rename(columns={'amount': 'volume'}, inplace=True)
            del df['code']
            del df['name']
            return df
        else:
            return None

# 添加 均线
def append_ma(df):
    for i in df.index:
        df.loc[i, 'ma1'] = df.loc[i, ['open', 'close', 'high', 'low']].mean()
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma30'] = df['close'].rolling(window=30).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    df['ma120'] = df['close'].rolling(window=120).mean()


def append_macd(df):
    df['DIF'], df['DEA'], df['MACD'] = tl.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)


# 添加 涨停和跌停价
def append_limit(df):
    df['high_limit'] = df['close'] * 1.11
    df['low_limit'] = df['close'] * 0.89


# 将date的格式转换成date和time
def exchange_time_to_date(df):
    df['date'] = df['time'].str[:10]


def append_bollard(df, timeperiod=50, nbdevup=1, nbdevdn=1, matype=0):
    '''
    添加Bolling带数据
    默认参数为：
        timeperiod=50
        nbdevup=1
        nbdevdn=1
        matype=0
    :param df: 
    :param timeperiod: 
    :param nbdevup: 
    :param nbdevdn: 
    :param matype: 
    :return: 
    '''
    df['upper'], df['middle'], df['lower'] = tl.BBANDS(
        df['close'].values,
        timeperiod=timeperiod,
        # number of non-biased standard deviations from the mean
        nbdevup=nbdevup,
        nbdevdn=nbdevdn,
        # Moving average type: simple moving average here
        matype=matype)


# 添加 close和均线是上升还是下降
def append_ma_direction(df):
    ma = ['close', 'ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'ma120']
    y_ma = ['y_' + i for i in ma]
    ma_dir_names = [i + '_dir' for i in ma]
    for i in range(len(ma)):
        df[y_ma[i]] = df[ma[i]].shift(1)
        df.loc[df[ma[i]].notnull() & df[y_ma[i]].notnull() & (df[ma[i]] > df[y_ma[i]]), ma_dir_names[i]] = 1
        df.loc[df[ma[i]].notnull() & df[y_ma[i]].notnull() & (df[ma[i]] == df[y_ma[i]]), ma_dir_names[i]] = 0
        df.loc[df[ma[i]].notnull() & df[y_ma[i]].notnull() & (df[ma[i]] < df[y_ma[i]]), ma_dir_names[i]] = -1
        del df[y_ma[i]]


def append_line_up_down(df):
    ma = ['close', 'ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'ma120']

    conditions = None
    for i in range(1, len(ma)):
        df.loc[:, 'line_' + str(i + 1) + '_up'] = -1
        df.loc[:, 'line_' + str(i + 1) + '_down'] = -1
        current_cond = (df[ma[i - 1]] > df[ma[i]]) & (df[ma[i - 1] + '_dir'] == 1) & (df[ma[i] + '_dir'] == 1)
        if conditions is None:
            conditions = current_cond
        else:
            conditions = conditions & current_cond
        df.loc[df[conditions].index, 'line_' + str(i + 1) + '_up'] = 1

        current_cond = (df[ma[i - 1]] < df[ma[i]]) & (df[ma[i - 1] + '_dir'] == -1) & (df[ma[i] + '_dir'] == -1)
        if conditions is None:
            conditions = current_cond
        else:
            conditions = conditions & current_cond
        df.loc[df[conditions].index, 'line_' + str(i + 1) + '_down'] = 1


def get_limit_date(df, win_s=2):
    '''
    根据收盘价，以win_s为窗口，计算两个窗口期前后的最大值和最小值。
    '''
    max = []
    min = []
    index = df.index.values
    for i in range(win_s, len(index) - win_s):
        if df.loc[index[i - win_s]:index[i - 1], 'close'].max() < df.loc[index[i], 'close'] and df.loc[
                                                                                                index[i + 1]:index[
                                                                                                    i + win_s],
                                                                                                'close'].max() < df.loc[
            index[i], 'close']:
            max.append(df.loc[index[i], 'date'])
        if df.loc[index[i - win_s]:index[i - 1], 'close'].min() > df.loc[index[i], 'close'] and df.loc[
                                                                                                index[i + 1]:index[
                                                                                                    i + win_s],
                                                                                                'close'].min() > df.loc[
            index[i], 'close']:
            min.append(df.loc[index[i], 'date'])
    return {'max': max, 'min': min}


def draw_limit(df, dates, limit='max'):
    #     if limit.startswith('max'):
    #         label = 'high'
    #     elif limit.startswith('min'):
    #         label = 'low'
    #     else:
    label = 'close'
    plt.figure(num=limit, figsize=(20, 10))
    x = pd.to_datetime(df['date'])
    y = df[label].values
    plt.plot(x, y, label=label)
    x0 = pd.to_datetime(dates[limit])
    y0 = []
    for date in dates[limit]:
        y0_value = df[df['date'] == date][label].values[0]
        x0_value = dt.datetime.strptime(date, '%Y-%m-%d')
        y0.append(y0_value)
        plt.annotate(date, xy=(x0_value, y0_value), xytext=(+5, +5), textcoords='offset points', rotation=45)
    plt.scatter(x0, y0, s=50, color='b')
    plt.show()


def output_trades(trades, name):
    # 使用shelve打开文件
    tmp_path = '/Users/jinkun.tian/gitee/financial_lab/strategy/tmp/'
    with shelve.open(os.path.join(tmp_path, name)) as db:
        db[name] = trades


def read_trades(name):
    tmp_path = '/Users/jinkun.tian/gitee/financial_lab/strategy/tmp/'
    with shelve.open(os.path.join(tmp_path, name)) as db:
        trades = db[name]
        return trades


def get_trades_line(df, trades):
    line = None
    for name in trades:
        trade_data = read_trades(name)
        # trades_df = Strategy.get_trades_df(df, trade_data)
        trades_df = pd.DataFrame(trade_data)
        trades_df = pd.merge(df, trades_df[['sell_day', 'own_money']], how='left', left_on='date', right_on='sell_day')[
            ['date', 'own_money']]
        line_current = get_line(trades_df, 'own_money', name, show_symbol=True, show_label=True, is_smooth=False)
        line_current.set_global_opts(datazoom_opts=opts.DataZoomOpts(range_start=0, range_end=100))

        if line is None:
            line = line_current
        else:
            line.overlap(line_current)
    return line

