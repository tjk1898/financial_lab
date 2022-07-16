import akshare as ak
import pandas as pd
import datetime as dt
import numpy as np
from util.logger import log


class Strategy:
    # 只适用于一只股票
    # 静态变量
    global_context = {
        'start_money': 10000,
        'money': 10000,  # 可用资金
        'security': None,  # 持有股票代码
        'volums': 0,  # 持有股票数量
        'trades': [],  # 交易-已经完成的 [{'buy_day':,'sell_day':,'profit':'title':,'own_money':}]
        'is_trading': False,  # 在交易中
        'buy_day': None,  # 买入日期
        'max_price': 0,  # 持有时的最高价
        'buy_price': 0  # 买入价格
    }

    @staticmethod
    def init():
        Strategy.global_context = {
            'start_money': 10000,
            'money': 10000,  # 可用资金
            'security': None,  # 持有股票代码
            'volums': 0,  # 持有股票数量
            'trades': [],  # 交易-已经完成的 [{'buy_day':,'sell_day':,'profit':'title':,'own_money':}]
            'is_trading': False,  # 在交易中
            'buy_day': None,  # 买入日期
            'max_price': 0,  # 持有时的最高价
            'buy_price': 0  # 买入价格
        }

    #
    context = {

    }

    def stop_profit(self, df, index):
        return False

    def stop_loss(self, df, index):
        return False

    def fill_data(self, df):
        pass

    def fill_data_m(self, df_d, df_m):
        pass

    def buy(self, df, index):
        '''
        is_trading = False and money>0才能买入
        '''
        pass

    def buy_data_process(self, df, index, buy_price):
        log.debug('买入时，开始对Strategy.global_context 进行处理')
        buy_day = df.loc[index, 'date']
        Strategy.global_context['is_trading'] = True
        Strategy.global_context['buy_day'] = buy_day
        money = Strategy.global_context['money']
        Strategy.global_context['volums'] = int(money / buy_price)
        Strategy.global_context['money'] = 0
        Strategy.global_context['buy_price'] = buy_price
        Strategy.global_context['max_price'] = buy_price
        log.debug("在调用buy方法后，Strategy的状态："+ str(Strategy.global_context))
        print("是log不管用了么？")

    def buy_m(self, df_d, index, df_m):
        pass

    def sell(self, df, index):
        '''
        is_trading = True：在交易中，才能卖出
        sell_day > buy_day才能卖出
        '''
        pass

    def sell_data_process(self, df, index, sell_price):
        sell_day = df.loc[index, 'date']
        volums = Strategy.global_context['volums']
        money = round((volums * sell_price), 2)
        buy_day = Strategy.global_context['buy_day']
        if len(Strategy.global_context['trades']) > 0:
            begin_money = Strategy.global_context['trades'][-1]['own_money']
        else:
            begin_money = Strategy.global_context['start_money']
        profit = round((money - begin_money), 2)
        title = str(profit)
        trade = {'buy_day': buy_day, 'sell_day': sell_day, 'profit': profit, 'own_money': money, 'title': title}
        Strategy.global_context['trades'].append(trade)
        Strategy.global_context['is_trading'] = False
        Strategy.global_context['buy_day'] = None
        Strategy.global_context['money'] = money


    def sell_m(self, df_d, index, df_m):
        pass

    @staticmethod
    def get_trades_df(df, trades):
        trades_df = pd.DataFrame(trades)
        trade_data = pd.merge(df['date'], trades_df[['sell_day', 'profit', 'own_money']], how='left', left_on='date',
                              right_on='sell_day', left_index=False, right_index=False, )

        last_profit = None
        last_own_money = Strategy.global_context['start_money']
        for i in trade_data.index:
            if pd.isna(trade_data.loc[i, 'profit']):
                trade_data.loc[i, 'profit'] = last_profit
            else:
                last_profit = trade_data.loc[i, 'profit']

            if pd.isna(trade_data.loc[i, 'own_money']):
                trade_data.loc[i, 'own_money'] = last_own_money
            else:
                last_own_money = trade_data.loc[i, 'own_money']
        return trade_data
