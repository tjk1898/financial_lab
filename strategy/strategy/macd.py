from strategy.Strategy import Strategy
from utils.util import *


class MacdV1(Strategy):
    '''
    抓暴力上升的股票
    '''

    def fill_data(self, df):
        append_bollard(df)
        append_ma(df)
        append_macd(df)

    def buy(self, df, index):
        # 昨天在布林带上线的下方，第一次触及了布林带上线，今天价格在布林带上线之上，按照最接近布林带的价格购买
        # 添加多头策略5日均线在10日均线之上
        if (df.loc[index - 1, 'upper'] < df.loc[index - 1, 'high']) \
                & (df.loc[index - 2, 'upper'] > df.loc[index - 2, 'high']) \
                & (df.loc[index - 1, 'upper'] < df.loc[index, 'high']) \
                & (df.loc[index - 1, 'ma5'] > df.loc[index - 1, 'ma10']):

            print("买入")

            # 如果开盘直接开在布林带之上，马上以开盘价买入
            # 否则按照upper价格买入
            if df.loc[index, 'open'] > df.loc[index - 1, 'upper']:
                buy_price = df.loc[index, 'open']
            else:
                buy_price = df.loc[index - 1, 'upper']

        self.buy_data_process(df, index, buy_price)

    def sell(self, df, index):
        # 已经买入，如果下穿上线，则卖出
        # 卖出价格，如果低开，开盘价低于upper，则使用open作为卖出价格，否则使用upper卖出
        if df.loc[index - 1, 'upper'] > df.loc[index, 'low']:
            print("卖出")
            if df.loc[index, 'open'] < df.loc[index - 1, 'upper']:
                sell_price = df.loc[index, 'open']
            else:
                sell_price = df.loc[index, 'upper']

        self.sell_data_process(df, index, sell_price)
