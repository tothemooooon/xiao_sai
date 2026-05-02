# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/dataapi"
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("1. 尝试获取股票列表:")
stocks = pro.stock_basic(exchange="SSE", list_status="L")
print(f"股票数量: {len(stocks)}")
if len(stocks) > 0:
    print(stocks.head())

print("\n2. 尝试获取交易日历:")
cal = pro.trade_cal(exchange="SSE", start_date="20240101", end_date="20251231")
print(f"交易日数量: {len(cal)}")
print(cal.head(10) if len(cal) > 0 else "无数据")

print("\n3. 尝试获取日线数据(使用股票代码):")
df = pro.daily(ts_code="000001.SZ", start_date="20250501", end_date="20250510")
print(f"行数: {len(df)}")
if len(df) > 0:
    print(df.head())
