#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/11/12 13:11 
@Author  : 
@File    : stock.py
@ProjectName: CRM 
'''
# pip install tushare pandas numpy

# import tushare as ts
# import pandas as pd
# import numpy as np
#
# # 请替换为你的Tushare Pro API Token
# ts.set_token('your_tushare_pro_api_token')
# pro = ts.pro_api()
#
# # 获取沪深市场的所有股票列表
# stock_list = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
#
# def get_stock_data(ts_code, start_date, end_date):
#     df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
#     return df.sort_values(by='trade_date')
#
# def calculate_momentum(df, period=120):
#     df['return'] = df['close'].pct_change(periods=period)
#     return df
#
# def apply_momentum_strategy(stock_list, start_date, end_date, period=120):
#     results = []
#     for index, row in stock_list.iterrows():
#         ts_code = row['ts_code']
#         try:
#             df = get_stock_data(ts_code, start_date, end_date)
#             df = calculate_momentum(df, period)
#             latest_return = df.iloc[-1]['return']
#             if not np.isnan(latest_return):
#                 results.append((ts_code, row['name'], latest_return))
#         except Exception as e:
#             print(f"Error processing {ts_code}: {e}")
#
#     # 将结果转换为DataFrame
#     result_df = pd.DataFrame(results, columns=['ts_code', 'name', 'latest_return'])
#     # 按照最新收益率降序排列
#     result_df = result_df.sort_values(by='latest_return', ascending=False)
#     return result_df
#
# start_date = '20230101'
# end_date = '20240101'
# momentum_period = 120  # 动量周期，例如120个交易日
#
# recommendations = apply_momentum_strategy(stock_list, start_date, end_date, momentum_period)
# print(recommendations.head(10))  # 输出推荐的前10只股票





import requests
import sched
import time
import json
import tkinter as tk
import threading
from datetime import datetime

# 初始化sched模块的scheduler类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
schedule = sched.scheduler(time.time, time.sleep)

def getData():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }

    text.delete(1.0, "end")
    print('开始获取数据...',text.delete(1.0, "end"))
    print(datetime.now())
    resultText = requests.get('https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol=HKHSTECH', headers=headers)
    print(resultText.text)
    data = json.loads(resultText.text)['data'][0]
    result ='恒生指数：' + '\n当前价格：' + str(data['current']) + ' ' + '\n幅度：' + str(data['percent']) + '%\n增长值：' + str(data['chg'])
    text.insert('insert', result)

    ## 中概互联
    resultTextB = requests.get('https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol=SH513050', headers=headers)
    print(resultTextB.text)
    dataB = json.loads(resultTextB.text)['data'][0]
    resultB ='\n\n中概互联：' + '\n当前价格：' + str(dataB['current']) + ' ' + '\n幅度：' + str(dataB['percent']) + '%\n增长值：' + str(dataB['chg'])
    text.insert('insert', resultB)

def task(inc):
    getData()
    schedule.enter(inc, 0, task, (inc,))


def func(inc=2):
    # enter四个参数分别为：
    # 间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数、给该触发函数的参数（tuple形式）
    schedule.enter(0, 0, task, (inc,))
    schedule.run()


# def insert_point():
#     code = entry.get()
#     text.delete(1.0, "end")
#     # text.insert('insert', var)
#     func()



if __name__ == '__main__':
    ## 可视化
    root_window = tk.Tk()
    root_window.title('  涨停  ')
    root_window.resizable(False,False)
    root_window.geometry('180x130')
    root_window["background"] = "#C9C9C9"
    ## 显示区域
    text = tk.Text(root_window, height=9)
    text.pack()
    ## 置顶
    root_window.attributes("-topmost", 1)
    root_window.attributes("-alpha", 0.8)
    root_window.attributes("-toolwindow", 2)
    ## 拿数据
    t1 = threading.Thread(target=func)
    t1.start()
    # 进入主循环，显示主窗口
    root_window.mainloop()
