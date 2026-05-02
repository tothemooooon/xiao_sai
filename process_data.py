# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

if not os.path.exists("E:/code/model/process_data"):
    os.makedirs("E:/code/model/process_data")

print("=" * 60)
print("读取原始数据")
print("=" * 60)

stock_list = pd.read_csv("E:/code/model/raw_data/stock_list.csv")
daily_data = pd.read_csv("E:/code/model/raw_data/daily_data.csv")

print(f"原始股票数量: {len(stock_list)}")
print(f"原始日交易数据行数: {len(daily_data)}")

stock_list["list_date"] = stock_list["list_date"].astype(str)

print("\n" + "=" * 60)
print("步骤1: 剔除ST股票和退市股票")
print("=" * 60)

st_codes = stock_list[stock_list["name"].str.contains("ST", na=False)][
    "ts_code"
].tolist()
delisted_codes = stock_list[stock_list["delist_date"].notna()]["ts_code"].tolist()

print(f"ST股票数量: {len(st_codes)}")
print(f"退市股票数量: {len(delisted_codes)}")

filtered_stocks = stock_list[~stock_list["ts_code"].isin(st_codes + delisted_codes)]
print(f"剔除ST和退市后的股票数量: {len(filtered_stocks)}")

print("\n" + "=" * 60)
print("步骤2: 剔除上市不足一年的新股")
print("=" * 60)

cutoff_date = "20250501"
new_stocks = filtered_stocks[filtered_stocks["list_date"] >= cutoff_date]
print(f"上市不足一年的新股数量: {len(new_stocks)}")

old_stocks = filtered_stocks[filtered_stocks["list_date"] < cutoff_date]
print(f"符合要求的股票数量: {len(old_stocks)}")

valid_codes = old_stocks["ts_code"].tolist()
print("\n" + "=" * 60)
print("步骤3: 筛选符合条件的数据")
print("=" * 60)

filtered_daily = daily_data[daily_data["ts_code"].isin(valid_codes)]
print(f"筛选后日交易数据行数: {len(filtered_daily)}")

filtered_daily = filtered_daily.sort_values(["ts_code", "trade_date"])
filtered_daily.to_csv(
    "E:/code/model/process_data/process_data.csv", index=False, float_format="%.4f"
)
print("\n处理后的数据已保存到 process_data/process_data.csv")

print("\n" + "=" * 60)
print("数据概览")
print("=" * 60)
print(f"总行数: {len(filtered_daily)}")
print(f"股票数量: {filtered_daily['ts_code'].nunique()}")
print(
    f"日期范围: {filtered_daily['trade_date'].min()} - {filtered_daily['trade_date'].max()}"
)
print(f"\n字段: {list(filtered_daily.columns)}")
print(f"\n前5行:\n{filtered_daily.head()}")
