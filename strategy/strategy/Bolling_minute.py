from strategy.Strategy import Strategy
from util.util import *

class Bolling_m_V1(Strategy):
    '''
    抓暴力上升的股票
    '''

    def fill_data_m(self, df_d, df_m):
        append_bollard(df_d)
        append_ma(df_d)
        append_limit(df_d)
        exchange_time_to_date(df_m)
        df_d.dropna(inplace=True)

    def buy_m(self, df_d, index, df_m):

        # 如果今天涨停，无法买入
        if df_d.loc[index - 1, 'close'] < df_d.loc[index, 'open'] and df_d.loc[index, 'high'] == df_d.loc[index, 'low']:
            return

        # 昨天的收盘价涨停价和跌停价如果包含了upper价格，今天开始按分钟跟踪，upper价格按照昨天的upper价格计算。
        # 如果今天涨跌停范围覆盖了昨天布林带的上线，则今天开始按分钟进行处理
        yesterday_upper = df_d.loc[index - 1, 'upper']
        # 如果昨天的最高价低于upper
        if (df_d.loc[index - 1, 'high_limit'] > df_d.loc[index - 1, 'upper']) \
                and (df_d.loc[index - 1, 'low_limit'] < df_d.loc[index - 1, 'upper']) \
                and (df_d.loc[index - 1, 'high'] < df_d.loc[index - 1, 'upper']):
            today_df_m = df_m[df_m['date'] == df_d.loc[index, 'date']]
            # 今天有close高于upper就买
            for i in today_df_m.index:
                close_price = today_df_m.loc[i, 'close']
                if close_price > yesterday_upper:
                    buy_df = close_price
                    Strategy.global_context['is_trading'] = True
                    Strategy.global_context['buy_day'] = df_d.loc[index, 'date']
                    money = Strategy.global_context['money']
                    Strategy.global_context['volums'] = int(money / buy_df)
                    Strategy.global_context['money'] = 0
                    return

    def sell_m(self, df_d, index, df_m):
        # 如果今天跌停，无法卖出
        if df_d.loc[index - 1, 'close'] > df_d.loc[index, 'open'] and df_d.loc[index, 'high'] == df_d.loc[index, 'low']:
            return
        # 只要最低价低于upper，就可能出现卖点
        yesterday_upper = df_d.loc[index - 1, 'upper']
        if (df_d.loc[index - 1, 'low_limit'] < yesterday_upper):
            today_df_m = df_m[df_m['date'] == df_d.loc[index, 'date']]

            for i in today_df_m.index:
                # 今天有close低于 lower 就卖出，按照close购卖
                close_price = today_df_m.loc[i, 'close']
                if close_price < yesterday_upper:
                    sell_df = close_price
                    volums = Strategy.global_context['volums']
                    money = round((volums * sell_df), 2)
                    buy_day = Strategy.global_context['buy_day']
                    sell_day = df_d.loc[index, 'date']
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
                    return
