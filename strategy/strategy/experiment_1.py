from utils.util import *
from utils.drawer import *
from Bolling import *
from Runner import Runner
from Strategy import Strategy


if __name__ == "__main__":
    # 数据获取
    # security = '601088'
    # start_day = '20210101'
    # end_day = '20220701'
    # price = get_price(security, str_start_date=start_day, str_end_date=end_day)

    price = pd.read_csv('/Users/jinkun.tian/gitee/financial_lab/AKshareTest/continue_rise/data/sh601088.csv')
    price.rename(columns={'amount':'turnover'},inplace=True)
    del price[price.columns[0]]

    #

    df = price.copy()
    df.dropna(inplace=True)


    # 初始化策略
    bollingV1 = BollingV1()
    bollingV2 = BollingV2()

    # 调用running
    runner = Runner()
    runner.df = df
    runner.strategys.append(bollingV1)
    runner.strategys.append(bollingV2)
    runner.start_index = 1

    runner.running()

    trades = bollingV1.global_context['trades']
    print(trades)
    k_graph = draw_K(df,trades=trades,width="1800px", height="800px")
    k_graph.render(path = "/Users/jinkun.tian/gitee/financial_lab/strategy/tmp/strategy12.html")





