# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/dataapi"
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("测试正确URL接口:")
for test_date in ["20250502", "20250505"]:
    df = pro.daily(trade_date=test_date)
    print(f"{test_date}: 行数={len(df)}")
    if len(df) > 0:
        print(f"列: {list(df.columns)}")
        print(df.head())
        break
