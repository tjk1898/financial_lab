import akshare as ak;
import pandas as pd;
import os;


# 获取行业股票
# 1. 房地产开发
fdckf_df = ak.stock_board_industry_cons_em("房地产开发")
print(fdckf_df)
# 2. 汽车整车
qczc_df = ak.stock_board_industry_cons_em("汽车整车")
print(qczc_df)
# 3. 汽车零部件
qclbj_df = ak.stock_board_industry_cons_em("汽车零部件")
print(qclbj_df)
# 4. 工程建设
gcjs_df = ak.stock_board_industry_cons_em("工程建设")
print(gcjs_df)
# 5. 半导体
bdt_df = ak.stock_board_industry_cons_em("半导体")
print(bdt_df)
# 6. 农牧饲渔
nmsy_df = ak.stock_board_industry_cons_em("农牧饲渔")
print(nmsy_df)
industry_list =[fdckf_df,qczc_df,qclbj_df,gcjs_df,bdt_df,nmsy_df]

stock_info = pd.read_csv('sock_all.csv')
def update_csv(stock_info,df):
    for stock_code in df["代码"]:
        try:
            stock_info = stock_info[stock_info["板块"]=="主板"]
            tmpe = stock_info[stock_info['代码'].str.contains(stock_code)].iloc[0][['代码','简称']]
            code = tmpe[0]
            name = tmpe[1]
            tmp_df = ak.stock_zh_index_daily_tx(code)
            tmp_df['code'] = code
            tmp_df['name'] = name
            print("输出的文件：" + code)
            tmp_df.to_csv("./industry/{}.csv".format(code),index=None)

        except:
            print("该股票不在主板中。")
            continue


for df in industry_list:
    update_csv(stock_info,df)

