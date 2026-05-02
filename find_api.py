# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/dataapi"
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("尝试获取分时数据...")
apis_to_try = [
    (
        "kline",
        {
            "ts_code": "000001.SZ",
            "start_date": "20250506",
            "end_date": "20250510",
            "freq": "5",
        },
    ),
    (
        "new_kline",
        {
            "ts_code": "000001.SZ",
            "start_date": "20250506",
            "end_date": "20250510",
            "freq": "5",
        },
    ),
    ("bk_tick", {"ts_code": "000001.SZ", "trade_date": "20250506"}),
    ("stk_tick", {"ts_code": "000001.SZ", "trade_date": "20250506"}),
    ("his_tick", {"ts_code": "000001.SZ", "trade_date": "20250506", "fields": "all"}),
]

for api_name, params in apis_to_try:
    try:
        func = getattr(pro, api_name)
        df = func(**params)
        if df is not None and len(df) > 0:
            print(f"\n{api_name}: 成功!")
            print(f"列: {list(df.columns)}")
            print(df.head(3))
            break
    except Exception as e:
        print(f"{api_name}: {str(e)[:50]}")
else:
    print("\n尝试获取所有可用API...")
    try:
        df = pro.fund_nav(ts_code="000001.SZ")
        print(f"fund_nav: {list(df.columns)}")
    except:
        pass

    try:
        df = pro.stk_relat(ts_code="000001.SZ")
        print(f"stk_relat: {list(df.columns)}")
    except:
        pass

print("\n检查完毕")
