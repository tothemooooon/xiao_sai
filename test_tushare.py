# -*- coding: utf-8 -*-
import tushare as ts
from tushare.pro import client as _ts_client
import pandas as pd
import os

_ts_client.DataApi._DataApi__http_url = "http://47.109.59.144:8989/datab api"

pro = ts.pro_api("hz4QxHCKdMwoSPXo8PMfLR3EZOnDqLsyJ576FilUyCE")

print("连接测试:")
df = pro.daily(trade_date="20260423")
print("columns=%s, rows=%d" % (list(df.columns), len(df)))
