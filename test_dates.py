# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/datab api"
pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("测试不同日期:")
for test_date in ["20250501", "20250502", "20250505", "20250506", "20250507"]:
    try:
        df = pro.daily(trade_date=test_date)
        print(f"{test_date}: 行数={len(df)}")
        if len(df) > 0:
            print(f"  列: {list(df.columns)}")
            print(f"  前3行:\n{df.head(3)}")
            break
    except Exception as e:
        print(f"{test_date}: 错误 - {e}")
