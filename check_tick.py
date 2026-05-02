# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd
import os

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/dataapi"
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("检查分时数据接口...")
print("\n1. 尝试minutely接口:")
try:
    df = pro.minutely(ts_code="000001.SZ", trade_date="20250506")
    print(f"minutely列: {list(df.columns)}")
    print(f"数据量: {len(df)}")
except Exception as e:
    print(f"失败: {e}")

print("\n2. 尝试daily接口:")
try:
    df = pro.daily(ts_code="000001.SZ", start_date="20250506", end_date="20250510")
    print(f"daily列: {list(df.columns)}")
    print(df)
except Exception as e:
    print(f"失败: {e}")

print("\n3. 尝试moneyflow接口:")
try:
    df = pro.moneyflow_hsgt(trade_date="20250506")
    print(f"moneyflow列: {list(df.columns)}")
except Exception as e:
    print(f"失败: {e}")

print("\n4. 尝试tick接口:")
try:
    df = pro.tick(ts_code="000001.SZ", trade_date="20250506")
    print(f"tick列: {list(df.columns)}")
    print(df.head())
except Exception as e:
    print(f"失败: {e}")
