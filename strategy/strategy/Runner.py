import pandas as pd
from strategy.Strategy import Strategy
from util.logger import log

class Runner():
    strategys = []
    df = pd.DataFrame()
    df_m = pd.DataFrame()
    start_index = 0

    def __init__(self, start_index=0):
        self.strategys = []
        self.df = pd.DataFrame()
        self.df_m = pd.DataFrame()
        self.start_index = start_index

    def running(self):

        for strategy in self.strategys:
            strategy.fill_data(self.df)

        for index in self.df.index[self.start_index:]:
            # 可以先卖出在买入
            sell_day = self.df.loc[index, 'date']
            for stratergy in self.strategys:
                if Strategy.global_context['is_trading']:
                    if sell_day > Strategy.global_context['buy_day']:
                        stop_lost = stratergy.stop_loss(self.df, index)
                        if not stop_lost:
                            log.debug(f'卖出时间:{sell_day}')
                            stratergy.sell(self.df, index)
                            log.debug('卖出后的状态：'+str(Strategy.global_context))
                        else:
                            print('强制平仓')
                    else:
                        break
                else:
                    break

            for stratergy in self.strategys:
                if Strategy.global_context['money'] > 0 and Strategy.global_context['is_trading'] == False:
                    log.debug('买入时间:'+self.df.loc[index, 'date'])
                    stratergy.buy(self.df, index)
                    log.debug('买入后的状态：'+str(Strategy.global_context))
                else:
                    break


    def running_m(self):

        for strategy in self.strategys:
            strategy.fill_data_m(self.df, self.df_m)

        for index in self.df.index[self.start_index:]:
            # print('处理数据：'+self.df.loc[index,'date'])
            for stratergy in self.strategys:
                if Strategy.global_context['money'] > 0 and Strategy.global_context['is_trading'] == False:
                    stratergy.buy_m(self.df, index, self.df_m)
                else:
                    break

            sell_day = self.df.loc[index, 'date']
            for stratergy in self.strategys:
                if Strategy.global_context['is_trading']:
                    if sell_day > Strategy.global_context['buy_day']:
                        stratergy.sell_m(self.df, index, self.df_m)
                    else:
                        break
                else:
                    break
