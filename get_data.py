# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd
import os
import time

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/dataapi"
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

print("\n步骤3: 获取日线数据...")
all_daily = []
for i, trade_date in enumerate(trade_dates):
    df = pro.daily(trade_date=trade_date)
    if df is not None and len(df) > 0:
        all_daily.append(df)
    if (i + 1) % 40 == 0:
        print(f"进度: {i + 1}/{len(trade_dates)}")
    time.sleep(0.02)

daily_data = pd.concat(all_daily, ignore_index=True)
daily_data.to_csv("E:/code/model/raw_data/daily_data.csv", index=False)
print(f"原始数据保存: {len(daily_data)}行")

print("\n步骤4: 处理数据...")
stock_list = pd.read_csv("E:/code/model/raw_data/stock_list.csv")
stock_list["list_date"] = stock_list["list_date"].astype(str)

st_codes = stock_list[stock_list["name"].str.contains("ST", na=False)][
    "ts_code"
].tolist()
delisted = stock_list[stock_list["delist_date"].notna()]["ts_code"].tolist()
cutoff = "20250501"
new_stocks = stock_list[stock_list["list_date"] >= cutoff]["ts_code"].tolist()

valid = stock_list[
    (~stock_list["ts_code"].isin(st_codes))
    & (~stock_list["ts_code"].isin(delisted))
    & (stock_list["list_date"] < cutoff)
]["ts_code"].tolist()

processed = daily_data[daily_data["ts_code"].isin(valid)].copy()
num_cols = [
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "change",
    "pct_chg",
    "vol",
    "amount",
]
for col in num_cols:
    if col in processed.columns:
        processed[col] = processed[col].round(4)

processed.to_csv("E:/code/model/process_data/process_data.csv", index=False)
print(f"处理后数据: {len(processed)}行, 股票数: {processed['ts_code'].nunique()}")

print("\n完成!")
print(f"原始数据: E:/code/model/raw_data/daily_data.csv")
print(f"处理后: E:/code/model/process_data/process_data.csv")
