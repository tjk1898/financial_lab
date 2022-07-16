import akshare as ak
import pandas as pd
import threading
from datetime import datetime
import os

if __name__ == '__main__':
    current_dir = os.getcwd()
    data_dir = os.path.join(current_dir, 'data')
    file_list = os.listdir(data_dir)

    stock_df = pd.DataFrame()
    for file in file_list:
        if file.endswith('.csv'):
            df = pd.read_csv(data_dir + '/' + file)
            stock_df = stock_df.append(df[['code','name','date','open','close','high','low','amount']])
    stock_df = stock_df.reset_index(drop=True)
    # 添加索引列
    stock_df.insert(0,'index_num',0)
    stock_df['index_num'] = stock_df.groupby('code').index_num.transform(lambda x: range(len(x)))
    # 计算涨幅
    stock_df['rise_rate'] = (stock_df['close'] - stock_df['open']) / stock_df['open']
    before_store_df = stock_df.copy(deep=True)
    before_store_df.rename(columns={"rise_rate":"before_rise_rate"},inplace=True)
    res_stock_df = pd.merge(stock_df,before_store_df[['code','index_num','before_rise_rate']],on=['code','index_num'],how='left')

    low_1 = datetime(2018, 6, 1)
    high_1 = datetime(2018, 8, 1)
    low_2 = datetime(2020, 3, 1)
    high_2 = datetime(2020, 5, 1)
    low_3 = datetime(2021, 3, 1)
    high_3 = datetime(2021, 5, 1)
    # 日期类型转换
    res_stock_df['date']=pd.to_datetime(stock_df['date'],format='%Y-%m-%d')
    stock_df_1 = res_stock_df[(res_stock_df['date']>low_1) & (res_stock_df['date']<high_1) & (res_stock_df['rise_rate']>0.1) & (res_stock_df['before_rise_rate']>0.1)]
    stock_df_2 = res_stock_df[(res_stock_df['date']>low_2) & (res_stock_df['date']<high_2) & (res_stock_df['rise_rate']>0.1) & (res_stock_df['before_rise_rate']>0.1)]
    stock_df_3 = res_stock_df[(res_stock_df['date']>low_3) & (res_stock_df['date']<high_3) & (res_stock_df['rise_rate']>0.1) & (res_stock_df['before_rise_rate']>0.1)]

    # 检查路径是否存在，如果不存在，就创建一个
    dir = current_dir+'/continue_rise/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    # 输出csv
    if len(stock_df_1) > 0:
        stock_df_1.to_csv(dir+'/20180601_20180801_continue_rise.csv',index=False)
    if len(stock_df_2) > 0:
        stock_df_2.to_csv(dir+'/20210301-20210501_continue_rise.csv',index=False)
    if len(stock_df_3) > 0:
        stock_df_3.to_csv(dir+'/20200301-20200501_continue_rise.csv',index=False)
