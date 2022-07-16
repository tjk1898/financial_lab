from util.logger import log
from util.util import *


class BollingV1(Strategy):
    '''
    抓超跌反弹的股票
    '''

    def fill_data(self, df):
        append_bollard(df)
        append_ma(df)

    def buy(self, df, index):
        if (df.loc[index, 'ma10'] < df.loc[index, 'ma1']) & (df.loc[index - 1, 'ma10'] > df.loc[index - 1, 'ma1']) & (
                df.loc[index, 'ma1'] < df.loc[index, 'lower']):
            buy_df = df.loc[index, 'ma1']
            Strategy.global_context['is_trading'] = True
            Strategy.global_context['buy_day'] = df.loc[index, 'date']
            money = Strategy.global_context['money']
            Strategy.global_context['volums'] = int(money / buy_df)
            Strategy.global_context['money'] = 0

    def sell(self, df, index):
        if df.loc[index, 'ma1'] < df.loc[index, 'ma10']:
            sell_df = df.loc[index, 'ma1']
            volums = Strategy.global_context['volums']
            money = round((volums * sell_df), 2)
            buy_day = Strategy.global_context['buy_day']
            sell_day = df.loc[index, 'date']
            if len(Strategy.global_context['trades']) > 0:
                begin_money = Strategy.global_context['trades'][-1]['own_money']
            else:
                begin_money = Strategy.global_context['start_money']

            profit = round((money - begin_money), 2)

            title = str(profit)

            trade = {'buy_day': buy_day, 'sell_day': sell_day, 'profit': profit, 'own_money': money, 'title': profit}
            Strategy.global_context['trades'].append(trade)
            Strategy.global_context['is_trading'] = False
            Strategy.global_context['buy_day'] = None
            Strategy.global_context['money'] = money


class BollingV2(Strategy):
    '''
    抓暴力上升的股票
    '''

    def fill_data(self, df):
        append_bollard(df)
        append_ma(df)

    def buy(self, df, index):
        if (df.loc[index, 'upper'] < df.loc[index, 'ma1']) & (df.loc[index - 1, 'upper'] > df.loc[index - 1, 'ma1']):
            buy_df = df.loc[index, 'ma1']
            Strategy.global_context['is_trading'] = True
            Strategy.global_context['buy_day'] = df.loc[index, 'date']
            money = Strategy.global_context['money']
            Strategy.global_context['volums'] = int(money / buy_df)
            Strategy.global_context['money'] = 0

    def sell(self, df, index):
        if df.loc[index, 'ma1'] < df.loc[index, 'upper']:
            sell_df = df.loc[index, 'ma1']
            volums = Strategy.global_context['volums']
            money = round((volums * sell_df), 2)
            buy_day = Strategy.global_context['buy_day']
            sell_day = df.loc[index, 'date']
            if len(Strategy.global_context['trades']) > 0:
                begin_money = Strategy.global_context['trades'][-1]['own_money']
            else:
                begin_money = Strategy.global_context['start_money']

            profit = round((money - begin_money), 2)

            title = str(profit)

            trade = {'buy_day': buy_day, 'sell_day': sell_day, 'profit': profit, 'own_money': money, 'title': profit}
            Strategy.global_context['trades'].append(trade)
            Strategy.global_context['is_trading'] = False
            Strategy.global_context['buy_day'] = None
            Strategy.global_context['money'] = money


class BollingV3(Strategy):
    '''
    抓暴力上升的股票
    '''

    def stop_loss(self, df, index):
        buy_price = Strategy.global_context['buy_price']
        max_price = Strategy.global_context['max_price']
        buy_price_lose_rate = 10
        max_price_lose_rate = 10

        Strategy.global_context['max_price'] = max(Strategy.global_context['max_price'], df.loc[index, 'high'])

        # TODO: 这种方法无法应对单日涨幅大于max_price_lose_rate的情况，因为不知道最高价出现的顺序，所以不清楚是涨到最高价还是从最高价跌下来的
        wline_price = max(buy_price * (1 - buy_price_lose_rate / 100), max_price * (1 - max_price_lose_rate / 100))
        if df.loc[index, 'low'] <= wline_price:
            # 开始平仓
            if df.loc[index, 'open'] <= wline_price:
                sell_price = df.loc[index, 'open']
            else:
                sell_price = wline_price
            self.sell_data_process(df, index, sell_price)
            return True
        else:
            return False

    def fill_data(self, df):
        append_bollard(df)
        append_ma(df)

    def buy(self, df, index):
        # 昨天在布林带上线的下方，第一次触及了布林带上线，今天价格在布林带上线之上，按照最接近布林带的价格购买
        # 添加多头策略5日均线在10日均线之上
        if (df.loc[index - 1, 'upper'] < df.loc[index - 1, 'high']) \
                & (df.loc[index - 2, 'upper'] > df.loc[index - 2, 'high']) \
                & (df.loc[index - 1, 'upper'] < df.loc[index, 'high']):

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
        if (df.loc[index - 1, 'upper'] > df.loc[index - 1, 'low']) \
                & (df.loc[index - 2, 'upper'] < df.loc[index - 2, 'low']) \
                & (df.loc[index - 1, 'upper'] > df.loc[index, 'low']):
            print("卖出")
            if df.loc[index, 'open'] < df.loc[index - 1, 'upper']:
                sell_df = df.loc[index, 'open']
            else:
                sell_df = df.loc[index, 'upper']
            volums = Strategy.global_context['volums']
            money = round((volums * sell_df), 2)
            buy_day = Strategy.global_context['buy_day']
            sell_day = df.loc[index, 'date']
            if len(Strategy.global_context['trades']) > 0:
                begin_money = Strategy.global_context['trades'][-1]['own_money']
            else:
                begin_money = Strategy.global_context['start_money']

            profit = round((money - begin_money), 2)

            title = str(profit)

            trade = {'buy_day': buy_day, 'sell_day': sell_day, 'profit': profit, 'own_money': money, 'title': profit}
            Strategy.global_context['trades'].append(trade)
            Strategy.global_context['is_trading'] = False
            Strategy.global_context['buy_day'] = None
            Strategy.global_context['money'] = money


class BollingV4(Strategy):
    '''
    抓暴力上升的股票
    '''

    def fill_data(self, df):
        append_bollard(df)
        append_ma(df)

    def buy(self, df, index):
        # 多头+布林带
        # 只要在布林带之上，而且呈现多头趋势，就可以买入
        # 添加多头策略5日均线在10日均线之上
        # | (df.loc[index - 2, 'upper'] > df.loc[index-2, 'high'])
        if ((df.loc[index - 1, 'upper'] > df.loc[index - 1, 'high'])) \
                & (df.loc[index - 1, 'upper'] < df.loc[index, 'high']) \
                & (df.loc[index - 1, 'ma5'] > df.loc[index - 1, 'ma10']):

            print("买入")
            # 如果开盘直接开在布林带之上，马上以开盘价买入
            # 否则按照upper价格买入
            if df.loc[index, 'open'] > df.loc[index - 1, 'upper']:
                buy_df = df.loc[index, 'open']
            else:
                buy_df = df.loc[index - 1, 'upper']
            Strategy.global_context['is_trading'] = True
            Strategy.global_context['buy_day'] = df.loc[index, 'date']
            money = Strategy.global_context['money']
            Strategy.global_context['volums'] = int(money / buy_df)
            Strategy.global_context['money'] = 0

    def sell(self, df, index):
        # 已经买入，如果下穿上线，则卖出
        # 卖出价格，如果低开，开盘价低于upper，则使用open作为卖出价格，否则使用upper卖出
        if (df.loc[index - 1, 'upper'] > df.loc[index, 'low']):
            # & (df.loc[index -1,'ma5']<df.loc[index -1,'ma10'])\

            print("卖出")
            if df.loc[index, 'open'] < df.loc[index - 1, 'upper']:
                sell_df = df.loc[index, 'open']
            else:
                sell_df = df.loc[index, 'upper']
            volums = Strategy.global_context['volums']
            money = round((volums * sell_df), 2)
            buy_day = Strategy.global_context['buy_day']
            sell_day = df.loc[index, 'date']
            if len(Strategy.global_context['trades']) > 0:
                begin_money = Strategy.global_context['trades'][-1]['own_money']
            else:
                begin_money = Strategy.global_context['start_money']

            profit = round((money - begin_money), 2)

            title = str(profit)

            trade = {'buy_day': buy_day, 'sell_day': sell_day, 'profit': profit, 'own_money': money, 'title': profit}
            Strategy.global_context['trades'].append(trade)
            Strategy.global_context['is_trading'] = False
            Strategy.global_context['buy_day'] = None
            Strategy.global_context['money'] = money


# 使用收盘价来判断
# 盈利：1.7w
#
class BollingV5(Strategy):
    '''
    '''
    '''
    买入：第一天触碰upper
    卖出：收盘价第一天低于upper，以收盘价卖出
    问题：如果第一天买入，第二天跌破upper，无法卖出
    '''

    def fill_data(self, df):
        append_bollard(df)
        append_ma(df)

    def buy(self, df, index):
        # 昨天在布林带上线的下方，第一次触及了布林带上线，今天价格在布林带上线之上，按照最接近布林带的价格购买
        if (df.loc[index - 1, 'upper'] < df.loc[index - 1, 'high']) \
                & (df.loc[index - 2, 'upper'] > df.loc[index - 2, 'high']) \
                & (df.loc[index - 1, 'upper'] < df.loc[index, 'high']):

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
        if (df.loc[index - 1, 'upper'] < df.loc[index - 1, 'close']) \
                & (df.loc[index, 'upper'] > df.loc[index, 'close']):
            print("卖出")
            sell_price = df.loc[index, 'close']
            self.sell_data_process(df, index, sell_price)


class BollingV6(Strategy):
    """
    5：
    买入：第一天触碰upper
    卖出：收盘价第一天低于upper，以收盘价卖出
    问题：如果第一天买入，第二天跌破upper，无法卖出，会持有很长时间，直到第二次波动
    6：
    修改：
    1. 
    将卖出条件修改只要收盘价低于upper，就以收盘价卖出
    问题：
    收益变为0.6K
    问题分析：
    卖出的太早，导致无法获取之后的利润
    """

    def fill_data(self, df):
        append_bollard(df)
        append_ma(df)

    def buy(self, df, index):
        # 昨天在布林带上线的下方，第一次触及了布林带上线，今天价格在布林带上线之上，按照最接近布林带的价格购买
        if (df.loc[index, 'upper'] < df.loc[index, 'close']) \
                & (df.loc[index, 'ma5'] > df.loc[index, 'ma20']) \
                & (df.loc[index - 1, 'ma20'] < df.loc[index, 'ma20']):
            # 如果开盘直接开在布林带之上，马上以开盘价买入
            # 否则按照upper价格买入
            if df.loc[index, 'open'] > df.loc[index - 1, 'upper']:
                buy_price = df.loc[index, 'open']
            else:
                buy_price = df.loc[index - 1, 'upper']
            try:
                Strategy.buy_data_process(df, index, buy_price)
                log.debug('买入后，Stratey的状态：'+str(Strategy.global_context))
            except Exception as e:
                log.error("open:" + str(df.loc[index, 'open']))
                log.error("upper:" + str(df.loc[index - 1, 'upper']))
                log.error(buy_price)
                raise e

    def sell(self, df, index):
        # 已经买入，如果下穿上线，则卖出
        # 卖出价格，如果低开，开盘价低于upper，则使用open作为卖出价格，否则使用upper卖出
        if df.loc[index, 'upper'] > df.loc[index, 'close']:
            # print("卖出")
            sell_price = df.loc[index, 'close']
            Strategy.sell_data_process(df, index, sell_price)
