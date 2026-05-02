# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd
import os
import time

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/dataapi"
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

if not os.path.exists("E:/code/model/raw_data"):
    os.makedirs("E:/code/model/raw_data")

print("=" * 60)
print("步骤1: 获取股票列表和交易日历")
print("=" * 60)

stocks = pro.stock_basic(exchange="SSE", list_status="L")
stocks_sz = pro.stock_basic(exchange="SZSE", list_status="L")
all_stocks = pd.concat([stocks, stocks_sz], ignore_index=True)
print(f"A股股票总数: {len(all_stocks)}")

cal = pro.trade_cal(
    exchange="SSE", start_date="20250501", end_date="20260430", is_open="1"
)
trade_dates = cal["cal_date"].tolist()
print(f"交易日数量: {len(trade_dates)}")

print("\n" + "=" * 60)
print("步骤2: 获取日线数据 (按日期批量获取)")
print("=" * 60)

all_daily = []
failed_dates = []

for i, trade_date in enumerate(trade_dates):
    try:
        df = pro.daily(trade_date=trade_date)
        if df is not None and len(df) > 0:
            all_daily.append(df)
            if (i + 1) % 20 == 0:
                print(
                    f"进度: {i + 1}/{len(trade_dates)} - {trade_date}, 股票数: {len(df)}"
                )
        else:
            failed_dates.append(trade_date)
    except Exception as e:
        print(f"获取 {trade_date} 失败: {e}")
        failed_dates.append(trade_date)
    time.sleep(0.1)

if all_daily:
    daily_data = pd.concat(all_daily, ignore_index=True)
    daily_data.to_csv("E:/code/model/raw_data/daily_data.csv", index=False)
    print(f"\n日交易数据已保存，总行数: {len(daily_data)}")
    print(f"失败日期数: {len(failed_dates)}")

print("\n完成!")
