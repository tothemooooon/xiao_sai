# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/dataapi"
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("尝试更多数据接口...")
test_apis = [
    ("stk_weather", {}),
    ("stock_zt_pool", {"trade_date": "20250506"}),
    ("zt_pool", {"trade_date": "20250506"}),
    ("daily_basic", {"trade_date": "20250506"}),
    ("stock_basic", {"exchange": "SSE"}),
]

for api_name, params in test_apis:
    try:
        func = getattr(pro, api_name)
        df = func(**params)
        if df is not None and len(df) > 0:
            print(f"\n{api_name}: 成功! {len(df)}行")
            print(f"列: {list(df.columns)[:8]}...")
    except Exception as e:
        if "daily" not in api_name and "basic" not in api_name:
            pass  # print(f"{api_name}: 不可用")
