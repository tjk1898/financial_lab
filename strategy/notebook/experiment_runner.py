from pyecharts.charts import *
from pyecharts.components import Table
from pyecharts.commons.utils import JsCode
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import os
from util.dicts import *
from util.drawer import *
import pandas as pd
from strategy.Strategy import Strategy
from strategy.Runner import Runner
from util.logger import log

class Experiment():
    '''

    '''
    '''
    用数据进行回测
    执行回测
    指定：
    1. 数据文件所在目录
    2. 策略
    3. 时间段
    运行：
    1. 加载数据
    2. 创建策略
    3. 执行回测
    4. 绘图
    5. 将结果保存在result中
    '''
    file_dir = '/Users/jinkun.tian/gitee/financial_lab/strategy/data/topbluechipes/'

    def __init__(self, strategy_class, file_dir=None, start_date=None, end_date=None):
        self.results = {}
        self.strategy_class = strategy_class
        self.start_date = start_date
        self.end_date = end_date
        if file_dir is not None:
            self.file_dir = file_dir

    def __get_df(self, code):
        file_list = os.listdir(self.file_dir)
        for file_name in file_list:
            if code in file_name:
                file_path = os.path.join(self.file_dir, file_name)
                price = pd.read_csv(file_path)
                price.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
                df = price[price['date'] > '2020-01-01']
                return df

    def trade(self, df):
        Strategy.init()
        # 调用running
        runner = Runner()
        strategy = self.strategy_class()
        runner.df = df
        runner.strategys.append(strategy)
        runner.start_index = 2
        runner.running()
        trades = Strategy.global_context['trades']
        return trades

    def run(self):
        file_list = os.listdir(self.file_dir)
        for file_name in file_list:
            log.info(f"procees:{file_name}")
            stock_name = stock_code_name[file_name[:6]]
            file_path = os.path.join(self.file_dir, file_name)
            df = pd.read_csv(file_path)
            df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
            if self.start_date is not None:
                df = df[df['date'] > self.start_date]
            if self.end_date is not None:
                df = df[df['date'] < self.end_date]
            try:
                # 获取交易信息
                trades = self.trade(df)
                # 获取交易图形
                if len(trades)>0:
                    k_graph, line = self.get_k_and_line(stock_name, df, trades)
                    self.results[file_name[:6]] = {'name': stock_name, 'trades': trades, 'k_graph': k_graph,
                                                'own_money_line': line}
                else:
                    self.results[file_name[:6]] = {'name': stock_name, 'trades': trades, 'k_graph': None,
                                                   'own_money_line': None}

            except Exception as e:
                log.error(file_path + '处理错误')
                log.exception(e)

    #     self.results.sort(key=self.__sort_fun(), reverse=True)
    #
    # def __sort_fun(self, e):
    #     if len(e['trades']) > 0:
    #         return e['trades'][-1]['own_money']
    #     else:
    #         return -10000000

    def get_k_and_line(self, stock_name, df, trades):
        own_money = trades[-1]['own_money']
        log.info(str(stock_name)+":" + str(own_money))
        k_graph = draw_K(df, trades=trades)

        trades_df = pd.DataFrame(trades)
        line_data = pd.merge(df, trades_df[['sell_day', 'own_money']], how='left', left_on='date', right_on='sell_day')[
            ['date', 'own_money']]

        line = get_line(line_data, 'own_money', name=stock_name, show_symbol=True, show_label=True, is_smooth=False)
        line.set_global_opts(datazoom_opts=opts.DataZoomOpts(range_start=10, range_end=80))
        return k_graph, line
