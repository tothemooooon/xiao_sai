# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd
import os
import time

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/dataapi"
_ts_client.DataApi.__timeout = 60
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

os.makedirs("E:/code/model/raw_data", exist_ok=True)
os.makedirs("E:/code/model/process_data", exist_ok=True)

print("步骤1: 获取股票列表...")
stocks = pro.stock_basic(exchange="SSE", list_status="L")
stocks_sz = pro.stock_basic(exchange="SZSE", list_status="L")
all_stocks = pd.concat([stocks, stocks_sz], ignore_index=True)
all_stocks.to_csv("E:/code/model/raw_data/stock_list.csv", index=False)
print(f"股票总数: {len(all_stocks)}")

print("\n步骤2: 获取交易日历...")
cal = pro.trade_cal(
    exchange="SSE", start_date="20250501", end_date="20260430", is_open="1"
)
trade_dates = cal["cal_date"].tolist()
cal.to_csv("E:/code/model/raw_data/trade_calendar.csv", index=False)
print(f"交易日: {len(trade_dates)}")

print("\n步骤3: 获取日线数据(带重试)...")
all_daily = []
retry_count = 3

for i, trade_date in enumerate(trade_dates):
    success = False
    for r in range(retry_count):
        try:
            df = pro.daily(trade_date=trade_date)
            if df is not None and len(df) > 0:
                all_daily.append(df)
                success = True
                break
        except Exception as e:
            if r < retry_count - 1:
                time.sleep(2)
            else:
                print(f"失败 {trade_date}: {e}")
    if (i + 1) % 40 == 0:
        print(f"进度: {i + 1}/{len(trade_dates)}")
    time.sleep(0.05)

daily_data = pd.concat(all_daily, ignore_index=True)
daily_data.to_csv("E:/code/model/raw_data/daily_data.csv", index=False)
print(f"原始数据保存: {len(daily_data)}行")

print("\n完成步骤3!")
print("请手动运行步骤4处理数据: python process_data.py")
