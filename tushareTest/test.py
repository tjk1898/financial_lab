# 本代码由可视化策略环境自动生成 2022年5月28日 16:15
# 本代码单元只能在可视化模式下编辑。您也可以拷贝代码，粘贴到新建的代码单元或者策略，然后修改。


# Python 代码入口函数，input_1/2/3 对应三个输入端，data_1/2/3 对应三个输出端
def m1_run_bigquant_run(input_1, input_2, input_3):
    # 示例代码如下。在这里编写您的代码
    df = input_1.read()
    lt = ['518880.HOF','513600.HOF','512880.HOF']
    df = df[(df['instrument']==lt[0])|(df['instrument']==lt[1])|(df['instrument']==lt[2])]

    data_1 = DataSource.write_df(df)
    return Outputs(data_1=data_1, data_2=None, data_3=None)

# 后处理函数，可选。输入是主函数的输出，可以在这里对数据做处理，或者返回更友好的outputs数据格式。此函数输出不会被缓存。
def m1_post_run_bigquant_run(outputs):
    return outputs

# Python 代码入口函数，input_1/2/3 对应三个输入端，data_1/2/3 对应三个输出端
def m3_run_bigquant_run(input_1, input_2, input_3):
    # 示例代码如下。在这里编写您的代码
    df = input_1.read()
    lt = '000300.HIX'
    df = df[df['instrument']==lt]

    data_1 = DataSource.write_df(df)
    return Outputs(data_1=data_1, data_2=None, data_3=None)

# 后处理函数，可选。输入是主函数的输出，可以在这里对数据做处理，或者返回更友好的outputs数据格式。此函数输出不会被缓存。
def m3_post_run_bigquant_run(outputs):
    return outputs

# Python 代码入口函数，input_1/2/3 对应三个输入端，data_1/2/3 对应三个输出端
def m6_run_bigquant_run(input_1, input_2, input_3):
    # 示例代码如下。在这里编写您的代码
    datadf = input_1.read()
    datadf_ind = input_2.read()

    history_ds = DataSource.write_df(pd.concat([datadf,datadf_ind],axis=0))
    return Outputs(data_1=history_ds, data_2=None, data_3=None)

# 后处理函数，可选。输入是主函数的输出，可以在这里对数据做处理，或者返回更友好的outputs数据格式。此函数输出不会被缓存。
def m6_post_run_bigquant_run(outputs):
    return outputs

# Python 代码入口函数，input_1/2/3 对应三个输入端，data_1/2/3 对应三个输出端
def m7_run_bigquant_run(input_1, input_2, input_3):
    # 示例代码如下。在这里编写您的代码
    start_date = '2017-11-27'
    end_date = '2018-09-05'
    bm_instruments = ['000300.HIX']
    start = pd.to_datetime(start_date)-datetime.timedelta(50)
    start = start.strftime('%Y-%m-%d')
    id_ohlc = 'bar1d_index_CN_STOCK_A'
    origin_fields=['open', 'high', 'low', 'close', 'volume', 'amount']
    ohlc_df = DataSource(id_ohlc).read(instruments=bm_instruments, start_date=start, end_date=end_date,
                                       fields=origin_fields)

    ohlc_df.rename({'s_dq_close':'close', 's_dq_high':'high', 's_dq_open':'open', 's_dq_low':'low', 's_dq_volume':'volume', 's_dq_amount':'amount'},axis=1, inplace=True)
    benchmark_ds = DataSource.write_df(ohlc_df)
    return Outputs(data_1=benchmark_ds, data_2=None, data_3=None)

# 后处理函数，可选。输入是主函数的输出，可以在这里对数据做处理，或者返回更友好的outputs数据格式。此函数输出不会被缓存。
def m7_post_run_bigquant_run(outputs):
    return outputs

def m5_initialize_bigquant_run(context):
    set_commission(futures_commission=PerContract(cost={'IC':(0.0023, 0.0015, 0.0023)}))
    set_need_settle(False)
    context.length_1 = 5
    context.length_2 = 20

def m5_handle_data_bigquant_run(context, data):

    #instrument = ['IC0000.CFX','IF0000.CFX','IH0000.CFX']
    instrument = ['518880.HOF','513600.HOF','512880.HOF']

    today = data.current_dt.strftime('%Y-%m-%d')

    sid_ind = symbol('000300.HIX')
    sid_a = future_symbol(instrument[0])
    sid_b = future_symbol(instrument[1])
    sid_c = future_symbol(instrument[2])

    # 最新价格
    #price = data.current(sid, 'price')
    position_a = context.portfolio.positions[sid_a]
    position_b = context.portfolio.positions[sid_b]
    position_c = context.portfolio.positions[sid_c]
    curr_position_a = position_a.amount
    curr_position_b = position_b.amount
    curr_position_c = position_c.amount
    ma5_ind_price = data.history(sid_ind, 'price', context.length_1, '1d').mean()
    ma20_ind_price = data.history(sid_ind, 'price', context.length_2, '1d').mean()


    if ma5_ind_price > ma20_ind_price:
        if data.can_trade(sid_a) and curr_position_a == 0 :
            order_target_percent(sid_a, 0.2)
            print(get_datetime(), 'buy_a')
            if data.can_trade(sid_b) and curr_position_b > 0:
                order_target_percent(sid_b, 0)
                print(get_datetime(), 'sell_b')
            elif data.can_trade(sid_c) and curr_position_c > 0:
                order_target_percent(sid_c, 0)
                print(get_datetime(), 'sell_c')

    elif ma5_ind_price < ma20_ind_price:
        if data.can_trade(sid_b) and curr_position_b == 0 :
            order_target_percent(sid_b, 0.2)
            print(get_datetime(), 'buy_b')
            if data.can_trade(sid_a) and curr_position_a > 0:
                order_target_percent(sid_a, 0)
                print('=='*10,curr_position_a)
                print(get_datetime(), 'sell_a')
            elif data.can_trade(sid_c) and curr_position_c > 0:
                order_target_percent(sid_c, 0)
                print(get_datetime(), 'sell_c')

    elif ma5_ind_price == ma20_ind_price:
        if data.can_trade(sid_c) and curr_position_c == 0 :
            order_target_percent(sid_c, 0.2)
            print(get_datetime(), 'buy_c')
            if data.can_trade(sid_a) and curr_position_a > 0:
                order_target_percent(sid_a, 0)
                print(get_datetime(), 'sell_a')
            elif data.can_trade(sid_b) and curr_position_b > 0:
                order_target_percent(sid_b, 0)
                print(get_datetime(), 'sell_b')
# 回测引擎：准备数据，只执行一次
def m5_prepare_bigquant_run(context):
    pass

# 回测引擎：每个单位时间开始前调用一次，即每日开盘前调用一次。
def m5_before_trading_start_bigquant_run(context, data):
    pass


m2 = M.use_datasource.v1(
    datasource_id='bar1d_CN_FUND',
    start_date='2017-11-27',
    end_date='2018-09-05'
)

m1 = M.cached.v3(
    input_1=m2.data,
    run=m1_run_bigquant_run,
    post_run=m1_post_run_bigquant_run,
    input_ports='',
    params='{}',
    output_ports=''
)

m4 = M.use_datasource.v1(
    datasource_id='bar1d_index_CN_STOCK_A',
    start_date='2017-11-27',
    end_date='2018-09-05'
)

m3 = M.cached.v3(
    input_1=m4.data,
    run=m3_run_bigquant_run,
    post_run=m3_post_run_bigquant_run,
    input_ports='',
    params='{}',
    output_ports=''
)

m6 = M.cached.v3(
    input_1=m1.data_1,
    input_2=m3.data_1,
    run=m6_run_bigquant_run,
    post_run=m6_post_run_bigquant_run,
    input_ports='',
    params='{}',
    output_ports=''
)

m7 = M.cached.v3(
    run=m7_run_bigquant_run,
    post_run=m7_post_run_bigquant_run,
    input_ports='',
    params='{}',
    output_ports=''
)

m8 = M.instruments.v2(
    start_date='2017-11-27',
    end_date='2018-09-05',
    market='CN_FUND',
    instrument_list='[\'518880.HOF\',\'513600.HOF\',\'512880.HOF\']',
    max_count=0
)

m5 = M.trade.v4(
    instruments=m8.data,
    history_ds=m6.data_1,
    benchmark_ds=m7.data_1,
    start_date='2018-01-16',
    end_date='2018-09-05',
    initialize=m5_initialize_bigquant_run,
    handle_data=m5_handle_data_bigquant_run,
    prepare=m5_prepare_bigquant_run,
    before_trading_start=m5_before_trading_start_bigquant_run,
    volume_limit=0.026,
    order_price_field_buy='open',
    order_price_field_sell='close',
    capital_base=2000,
    auto_cancel_non_tradable_orders=True,
    data_frequency='daily',
    price_type='真实价格',
    product_type='股票',
    plot_charts=True,
    backtest_only=False,
    benchmark=''
)