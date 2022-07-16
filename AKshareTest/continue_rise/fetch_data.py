import akshare as ak
import pandas as pd

if __name__ == '__main__':
    all_stock= pd.read_csv("sock_all.csv")
    zb_all_stock=all_stock[all_stock["板块"]=="主板"]
    zb_all_stock = zb_all_stock.reset_index(drop=True)
    for i in range(927,len(zb_all_stock)):
        stock_info = zb_all_stock.loc[i]
        code = stock_info['代码']
        name = stock_info['简称']
        try:
            tmp_df = ak.stock_zh_index_daily_tx(code)
            tmp_df['code'] = code
            tmp_df['name'] = name
            tmp_df.to_csv("{}/{}.csv".format('data',code))
        except:
            print("获取数据出错",i,code,name)
            break;