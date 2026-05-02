# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd
import os

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/dataapi"
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("=" * 60)
print("步骤1: 获取股票列表")
print("=" * 60)

stocks = pro.stock_basic(exchange="SSE", list_status="L")
print(f"上海股票数量: {len(stocks)}")

stocks_sz = pro.stock_basic(exchange="SZSE", list_status="L")
print(f"深圳股票数量: {len(stocks_sz)}")

all_stocks = pd.concat([stocks, stocks_sz], ignore_index=True)
print(f"总股票数量: {len(all_stocks)}")

stock_list = all_stocks[
    ["ts_code", "symbol", "name", "list_date", "delist_date", "is_hs"]
]
stock_list.to_csv("E:/code/model/raw_data/stock_list.csv", index=False)
print(f"股票列表已保存")

print("\n" + "=" * 60)
print("步骤2: 获取交易日历")
print("=" * 60)

cal = pro.trade_cal(
    exchange="SSE", start_date="20250501", end_date="20260430", is_open="1"
)
trade_dates = cal["cal_date"].tolist()
print(f"交易日数量: {len(trade_dates)}")
print(f"交易日范围: {trade_dates[0]} - {trade_dates[-1]}")
cal.to_csv("E:/code/model/raw_data/trade_calendar.csv", index=False)

print("\n" + "=" * 60)
print("步骤3: 获取全部A股日交易数据")
print("=" * 60)

ts_codes = stock_list["ts_code"].tolist()
print(f"需要获取的股票代码数量: {len(ts_codes)}")

all_daily = []
batch_size = 100

for i in range(0, len(ts_codes), batch_size):
    batch_codes = ts_codes[i : i + batch_size]
    for ts_code in batch_codes:
        try:
            df = pro.daily(ts_code=ts_code, start_date="20250501", end_date="20260430")
            if df is not None and len(df) > 0:
                all_daily.append(df)
        except Exception as e:
            print(f"获取 {ts_code} 失败: {e}")
    print(f"进度: {min(i + batch_size, len(ts_codes))}/{len(ts_codes)}")

if all_daily:
    daily_data = pd.concat(all_daily, ignore_index=True)
    daily_data.to_csv("E:/code/model/raw_data/daily_data.csv", index=False)
    print(f"\n日交易数据已保存，总行数: {len(daily_data)}")
else:
    print("未获取到任何数据")
