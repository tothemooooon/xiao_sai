# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/datab api"
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("获取日线数据(单日):")
df = pro.daily(trade_date="20260501")
print(f"行数: {len(df)}")
print(f"列: {list(df.columns) if len(df) > 0 else 'None'}")
if len(df) > 0:
    print(df.head())
