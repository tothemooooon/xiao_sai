# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd

lg = bs.login()
print(f"登录: {lg.error_msg}")

print("\n获取分时数据...")
rs = bs.query_history_k_data_plus(
    "sz.000001",
    "date,time,open,high,low,close,volume",
    start_date="2025-05-06",
    end_date="2025-05-10",
    frequency="5",  # 5分钟线
    adjustflag="2",
)

data_list = []
while (rs.error_code == "0") & rs.next():
    data_list.append(rs.get_row_data())

if data_list:
    df = pd.DataFrame(data_list, columns=rs.fields)
    print(f"成功获取{len(df)}条")
    print(df.head(10))
else:
    print("获取失败")

bs.logout()
