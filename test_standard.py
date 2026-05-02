# -*- coding: utf-8 -*-
import tushare as ts
import pandas as pd

pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("测试标准接口:")
df = pro.daily(trade_date="20250502")
print(f"行数: {len(df)}")
if len(df) > 0:
    print(f"列: {list(df.columns)}")
    print(df.head())
