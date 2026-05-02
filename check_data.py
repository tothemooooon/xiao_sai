# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd
import os

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/datab api"
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("1. 获取交易日历:")
cal = pro.trade_cal(
    exchange="SSE", start_date="20250501", end_date="20260430", is_open="1"
)
print(f"交易日数量: {len(cal)}")
print(cal.head())
print("\n2. 获取股票列表:")
stocks = pro.stock_basic(exchange="SSE", list_status="L")
print(f"股票数量: {len(stocks)}")
print(stocks.head())
