# -*- coding: utf-8 -*-
import pandas as pd

df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])

# 查看涨停后次日的数据分布
df_zt = df[df["pct_chg"] >= 9.9].copy()
df_zt["next_pct"] = df_zt.groupby("ts_code")["pct_chg"].shift(-1)
df_zt = df_zt.dropna(subset=["next_pct"])

print("涨停后次日涨幅分布:")
print(df_zt["next_pct"].describe())
print("\n分布统计:")
print(f" > 0: {(df_zt['next_pct'] > 0).sum()}")
print(f" = 0: {(df_zt['next_pct'] == 0).sum()}")
print(f" < 0: {(df_zt['next_pct'] < 0).sum()}")

print("\n次日本身涨跌分布:")
print(df_zt["next_pct"].value_counts().head(20))
