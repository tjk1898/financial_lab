from pyecharts.charts import *
from pyecharts import options as opts
from pyecharts.globals import ThemeType


def get_line(df, column, name=None, show_symbol=False, show_label=False, is_smooth=True):
    if name is None:
        name = column
    x_data = df['date'].values.tolist()
    y_data = df[column].values.tolist()
    return (Line()
            .add_xaxis(x_data)
            .add_yaxis(name,
                       y_data,
                       label_opts=opts.LabelOpts(is_show=show_label),
                       is_symbol_show=show_symbol,
                       is_smooth=is_smooth,
                       is_connect_nones=True))


# 绘制K线图
def draw_K(df, extend_lines=None, down_graf=None, trades=None, width="900px", height="580px"):
    '''
    默认上图绘制 K线，bolling带，ma1，ma5，ma10，ma20。下图绘制 成交量
    :param df: 必须包括[date,open,close,high,low,turnover]，date格式需要是%Y-%m-%d
    :param extend_lines: 在K线上，扩展其他的线。可以调用get_line来实现。
    :param down_graf: 默认是交易量。也可以传入其他的图形，需要和K线保持相同的x轴。
    :param trades: 交易列表，需要的格式为[{'buy_day':,'sell_day':,'title':}]，可以为空。
    :return: K线图
    '''

    # 修改数据
    price = df

    # 绘制 K 线
    y_data = price[['open', 'close', 'high', 'low']].values.tolist()
    x_data = price['date'].values.tolist()
    kline = (Kline()
             .add_xaxis(x_data)
             .add_yaxis('K线', y_data)
             )
    kline.set_global_opts(datazoom_opts=[  # 缩放选项
        opts.DataZoomOpts(
            is_show=False,
            type_="inside",
            xaxis_index=[0, 1],
            # 初始的框选范围
            range_start=0,
            range_end=100,
        ),
        opts.DataZoomOpts(
            is_show=True,
            xaxis_index=[0, 1],
            type_="slider",
            pos_top="95%",
            range_start=0,
            range_end=100,
        )
    ])
    # 添加交易
    if trades is not None:
        mark_data = []
        for trade in trades:
            mark_data.append(opts.MarkAreaItem(name=str(trade['title']), x=(trade['buy_day'], trade['sell_day'])))
        kline.set_series_opts(markarea_opts=opts.MarkAreaOpts(data=mark_data,
                                                              itemstyle_opts=opts.ItemStyleOpts(opacity=0.3,  # 透明度
                                                                                                color={
                                                                                                    "type": 'linear',
                                                                                                    "x": 1, "y": 1,
                                                                                                    "x2": 0, "y2": 0,
                                                                                                    "colorStops": [
                                                                                                        {"offset": 0,
                                                                                                         "color": '#F55555'},
                                                                                                        {"offset": 1,
                                                                                                         "color": '#FCCF31'}]
                                                                                                }
                                                                                                )))

    # 绘制bolling线，并添加到K线
    up_data = price['upper'].values
    lower_data = price['lower'].values
    middle_data = price['middle'].values

    up_line = get_line(df, 'upper', "上引线")
    lower_line = get_line(df, 'lower', '下引线')
    middle_line = get_line(df, 'middle', '中线')
    kline.overlap(up_line)
    kline.overlap(lower_line)
    kline.overlap(middle_line)

    # 绘制均线，并添加到K线
    ma1_line = get_line(df, 'ma1', 'MA1')
    kline.overlap(ma1_line)
    ma5_line = get_line(df, 'ma5', 'MA5')
    kline.overlap(ma5_line)
    ma10_line = get_line(df, 'ma10', 'MA10')
    kline.overlap(ma10_line)
    ma20_line = get_line(df, 'ma20', 'MA20')
    kline.overlap(ma20_line)

    # 添加扩展线
    if extend_lines is not None:
        for line in extend_lines:
            kline.overlap(line)

    # 绘制成交量
    bar = (Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
           .add_xaxis(x_data)
           .add_yaxis('成交量', price['volume'].tolist(), label_opts=opts.LabelOpts(is_show=False))
           .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
           )

    # 整合大图
    itheme = "light"

    if down_graf is None:
        down_graf = bar

    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width=width, height=height,
            animation_opts=opts.AnimationOpts(animation=True, animation_easing="linear"),
            theme=itheme, page_title="Pyecharts_Demo",
        )
    )

    # 添加上图
    grid_chart.add(
        kline,
        grid_opts=opts.GridOpts(pos_left="1%", pos_right="1%", height="60%"),
    )

    # 添加下图
    grid_chart.add(
        down_graf,
        grid_opts=opts.GridOpts(pos_left="1%", pos_right="1%", pos_top="75%", height="16%"),
    )
    return grid_chart
