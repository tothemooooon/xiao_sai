# -*- coding: utf-8 -*-
import pandas as pd
import os

os.makedirs("E:/code/model/process_data", exist_ok=True)

print("读取原始数据...")
stock_list = pd.read_csv("E:/code/model/raw_data/stock_list.csv")
daily_data = pd.read_csv("E:/code/model/raw_data/daily_data.csv")
print(f"原始股票: {len(stock_list)}行")
print(f"原始日交易数据: {len(daily_data)}行")

print("\n处理数据...")
stock_list["list_date"] = stock_list["list_date"].astype(str)

st_codes = stock_list[stock_list["name"].str.contains("ST", na=False)][
    "ts_code"
].tolist()
cutoff = "20250501"
new_stocks = stock_list[stock_list["list_date"] >= cutoff]["ts_code"].tolist()

print(f"ST股票: {len(st_codes)}")
print(f"新股(不足一年): {len(new_stocks)}")

valid = stock_list[
    (~stock_list["ts_code"].isin(st_codes)) & (stock_list["list_date"] < cutoff)
]["ts_code"].tolist()

print(f"符合条件股票: {len(valid)}")

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
print(f"\n处理后数据: {len(processed)}行")
print(f"股票数: {processed['ts_code'].nunique()}")
print(f"日期范围: {processed['trade_date'].min()} - {processed['trade_date'].max()}")

print("\n完成!")
