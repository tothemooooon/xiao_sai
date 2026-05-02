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

print("=" * 60)
print("步骤1: 获取股票列表")
print("=" * 60)

stocks = pro.stock_basic(exchange="SSE", list_status="L")
stocks_sz = pro.stock_basic(exchange="SZSE", list_status="L")
all_stocks = pd.concat([stocks, stocks_sz], ignore_index=True)
all_stocks.to_csv("E:/code/model/raw_data/stock_list.csv", index=False)
print(f"A股股票总数: {len(all_stocks)}")

print("\n" + "=" * 60)
print("步骤2: 获取交易日历")
print("=" * 60)

cal = pro.trade_cal(
    exchange="SSE", start_date="20250501", end_date="20260430", is_open="1"
)
trade_dates = cal["cal_date"].tolist()
cal.to_csv("E:/code/model/raw_data/trade_calendar.csv", index=False)
print(f"交易日数量: {len(trade_dates)}")

print("\n" + "=" * 60)
print("步骤3: 按日期批量获取日线数据")
print("=" * 60)

all_daily = []
for i, trade_date in enumerate(trade_dates):
    try:
        df = pro.daily(trade_date=trade_date)
        if df is not None and len(df) > 0:
            all_daily.append(df)
            if (i + 1) % 50 == 0:
                print(f"进度: {i + 1}/{len(trade_dates)}")
    except Exception as e:
        print(f"获取 {trade_date} 失败: {e}")
    time.sleep(0.05)

daily_data = pd.concat(all_daily, ignore_index=True)
daily_data.to_csv("E:/code/model/raw_data/daily_data.csv", index=False)
print(f"\n原始数据已保存，总行数: {len(daily_data)}")

print("\n" + "=" * 60)
print("步骤4: 处理数据 - 剔除ST、退市、新股")
print("=" * 60)

stock_list = pd.read_csv("E:/code/model/raw_data/stock_list.csv")
stock_list["list_date"] = stock_list["list_date"].astype(str)

st_codes = stock_list[stock_list["name"].str.contains("ST", na=False)][
    "ts_code"
].tolist()
delisted_codes = stock_list[stock_list["delist_date"].notna()]["ts_code"].tolist()
remove_codes = list(set(st_codes + delisted_codes))
print(f"剔除ST和退市股票: {len(remove_codes)}")

cutoff_date = "20250501"
new_stocks = stock_list[stock_list["list_date"] >= cutoff_date]["ts_code"].tolist()
print(f"剔除上市不足一年新股: {len(new_stocks)}")

valid_codes = stock_list[
    (~stock_list["ts_code"].isin(remove_codes))
    & (stock_list["list_date"] < cutoff_date)
]["ts_code"].tolist()
print(f"符合条件股票数量: {len(valid_codes)}")

processed_data = daily_data[daily_data["ts_code"].isin(valid_codes)]
processed_data = processed_data.sort_values(["ts_code", "trade_date"])

for col in [
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "change",
    "pct_chg",
    "vol",
    "amount",
]:
    if col in processed_data.columns:
        processed_data[col] = processed_data[col].round(4)

processed_data.to_csv("E:/code/model/process_data/process_data.csv", index=False)
print(f"\n处理后数据已保存: {len(processed_data)} 行")

print("\n完成!")
print(f"原始数据: raw_data/daily_data.csv")
print(f"处理后数据: process_data/process_data.csv")
