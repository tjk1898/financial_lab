#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2021/7/31 16:26
Desc: 东方财富网-数据中心-资金流向
http://data.eastmoney.com/zjlx/detail.html
"""
import json
import time

import pandas as pd
import requests
import akshare as ak
from datetime import date
import mplfinance as mpf

sector_map = {
    "包装材料": "BK0733",
    "保险": "BK0474",
    "半导体": "BK1036",
    "玻璃玻纤": "BK0546",
    "船舶制造": "BK0729",
    "采掘行业": "BK1017",
    "电力行业": "BK0428",
    "多元金融": "BK0738",
    "电子元件": "BK0459",
    "电机": "BK1030",
    "电源设备": "BK1034",
    "电网设备": "BK0457",
    "电池": "BK1033",
    "电子化学品": "BK1039",
    "纺织服装": "BK0436",
    "非金属材料": "BK1020",
    "风电设备": "BK1032",
    "房地产开发": "BK0451",
    "房地产服务": "BK1045",
    "公用事业": "BK0427",
    "钢铁行业": "BK0479",
    "工程建设": "BK0425",
    "贵金属": "BK0732",
    "工程咨询服务": "BK0726",
    "光伏设备": "BK1031",
    "光学光电子": "BK1038",
    "工程机械": "BK0739",
    "航天航空": "BK0480",
    "化纤行业": "BK0471",
    "化肥行业": "BK0731",
    "化学制品": "BK0538",
    "化学原料": "BK1019",
    "环保行业": "BK0728",
    "化学制药": "BK0465",
    "互联网服务": "BK0447",
    "航空机场": "BK0420",
    "航运港口": "BK0450",
    "交运设备": "BK0429",
    "家电行业": "BK0456",
    "教育": "BK0740",
    "家用轻工": "BK0440",
    "计算机设备": "BK0735",
    "旅游酒店": "BK0485",
    "煤炭行业": "BK0437",
    "美容护理": "BK1035",
    "贸易行业": "BK0484",
    "农牧饲渔": "BK0433",
    "农药兽药": "BK0730",
    "酿酒行业": "BK0477",
    "能源金属": "BK1015",
    "汽车服务": "BK1016",
    "汽车整车": "BK1029",
    "汽车零部件": "BK0481",
    "燃气": "BK1028",
    "软件开发": "BK0737",
    "食品饮料": "BK0438",
    "石油行业": "BK0464",
    "商业百货": "BK0482",
    "水泥建材": "BK0424",
    "塑料制品": "BK0454",
    "生物制品": "BK1044",
    "通信设备": "BK0448",
    "通信服务": "BK0736",
    "通用设备": "BK0545",
    "铁路公路": "BK0421",
    "文化传媒": "BK0486",
    "物流行业": "BK0422",
    "橡胶制品": "BK1018",
    "小金属": "BK1027",
    "消费电子": "BK1037",
    "仪器仪表": "BK0458",
    "有色金属": "BK0478",
    "银行": "BK0475",
    "医疗器械": "BK1041",
    "医疗服务": "BK0727",
    "医药商业": "BK1042",
    "游戏": "BK1046",
    "造纸印刷": "BK0470",
    "专用设备": "BK0910",
    "珠宝首饰": "BK0734",
    "综合行业": "BK0539",
    "装修装饰": "BK0725",
    "装修建材": "BK0476",
    "证券": "BK0473",
    "中药": "BK1040",
    "专业服务": "BK1043"
}


def stock_sector_fund_flow_history(
        sector_name: str = "半导体") -> pd.DataFrame:
    """
    获得行业的历史资金流入
    :param sector_name:
    :return:
    """
    code = sector_map.get(sector_name)

    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    }
    params = {
        "cb": "jQuery112308203198908102463_1650786912611",
        "lmt": "0",
        "klt": "101",
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "secid": "90." + code,
        "_": int(time.time() * 1000)
    }
    r = requests.get(url, params=params, headers=headers)
    text_data = r.text
    json_data = json.loads(text_data[text_data.find("{"): -2])
    temp_df = pd.DataFrame(json_data["data"]["klines"])
    temp_df = temp_df[0].str.split(",", expand=True)
    temp_df.columns = ['日期', '主力净流入', '小单净流入', '中单净流入', '大单净流入', '超大单净流入', '主力净流入占比', '小单净流入占比', '中单净流入占比', '大单净流入占比',
                       '超大单净流入占比', '指数', '涨幅', '', '']
    return temp_df


def stock_sector_fund_flow_history_all() -> pd.DataFrame:
    result = pd.DataFrame();
    for key in sector_map.keys():
        df = stock_sector_fund_flow_history(key)
        df["行业名称"] = key;
        df["行业编码"] = sector_map.get(key);
        result = result.append(df, ignore_index=True)

    return result[
        ['行业编码', '行业名称', '日期', '主力净流入', '小单净流入', '中单净流入', '大单净流入', '超大单净流入', '主力净流入占比', '小单净流入占比', '中单净流入占比', '大单净流入占比',
         '超大单净流入占比', '指数', '涨幅']]


def print_K_line(stock_code: str = "sh601398", start_time: str = "2018-05-01", end_time: str = "2018-12-30"):
    """
    绘制K线图
    :param stock_code: "sh601398"
    :param start_time: "2018-05-01"
    :param end_time: "2018-12-30"
    :return:
    """
    # print("股票K线", stock_code, "开始时间：", start_time, "结束时间：", end_time)
    start_time = start_time.replace("-", "")
    end_time = end_time.replace("-", "")
    df = ak.stock_zh_a_daily(stock_code, start_time, end_time, adjust="qfq")
    df.set_index('date', inplace=True)
    mpf.plot(data=df)


def get_sz_index_daily(start_time: str = "2018-05-01", end_time: str = "2018-12-30"):
    """
    获取大盘K线图
    :param start_time: "2018-05-01"
    :param end_time: "2018-12-30"
    :return:
    """
    print("上证K线 ", "开始时间：", start_time, "结束时间：", end_time)
    stock_zh_index_daily_df = ak.stock_zh_index_daily(symbol="sh000001")
    stock_zh_index_daily_df.set_index('date', inplace=True)
    start = date.fromisoformat(start_time)
    end = date.fromisoformat(end_time)
    stock_zh_index_daily_df = stock_zh_index_daily_df[start:end]
    stock_zh_index_daily_df.index = pd.to_datetime(stock_zh_index_daily_df.index)
    mpf.plot(data=stock_zh_index_daily_df)



if __name__ == "__main__":
    # df = stock_sector_fund_flow_history_all()
    # print(df)

    start_time='2022-04-01'
    end_time='2022-04-26'
    print_K_line("sz000046",start_time,end_time)
