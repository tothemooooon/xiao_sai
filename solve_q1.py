# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

print("读取处理后数据...")
df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])

print(f"数据行数: {len(df)}")
print(f"股票数: {df['ts_code'].nunique()}")
print(f"日期范围: {df['trade_date'].min()} - {df['trade_date'].max()}")

# ========== 问题1: 涨停分析 ==========
print("\n" + "=" * 60)
print("问题1: 涨停次日走势分析")
print("=" * 60)

# 计算涨跌幅（基于前一日收盘价）
df["pct_chg_calc"] = ((df["close"] - df["pre_close"]) / df["pre_close"] * 100).round(4)

# 判断是否为涨停/跌停 (主板10%, 创业板20%)
df["is_zting"] = df["pct_chg_calc"] >= 9.9  # 主板涨停
df["is_dting"] = df["pct_chg_calc"] <= -9.9  # 主板跌停

# 获取下一天的数据
df["next_pct_chg"] = df.groupby("ts_code")["pct_chg_calc"].shift(-1)

# 主板涨停次日分析 (排除ST)
df_main = df[
    df["ts_code"].str.endswith(".SH")
    | df["ts_code"].str.startswith("600")
    | df["ts_code"].str.startswith("601")
    | df["ts_code"].str.startswith("603")
]
df_main = df_main[df_main["is_zting"] == True]


# 分类次日涨幅
def classify_change(x):
    if pd.isna(x):
        return "无数据"
    if x >= 9.9:
        return "涨停"
    elif x > 7:
        return "涨幅>7%"
    elif x > 5:
        return "5~7%"
    elif x > 3:
        return "3~5%"
    elif x > 0:
        return "0~3%"
    elif x > -3:
        return "-3~0%"
    elif x > -5:
        return "-5~-3%"
    elif x > -7:
        return "-7~-5%"
    elif x > -10:
        return "<-7%"
    elif x <= -9.9:
        return "跌停"
    return "其他"


df_main["next_category"] = df_main["next_pct_chg"].apply(classify_change)
result1 = df_main["next_category"].value_counts()
print("\n主板涨停次日分布:")
print(result1)

# 创业板涨停 (000/300开头)
df_cyb = df[df["ts_code"].str.startswith("000") | df["ts_code"].str.startswith("300")]
df_cyb = df_cyb[df_cyb["is_zting"] == True]
df_cyb["next_category"] = df_cyb["next_pct_chg"].apply(classify_change)
result1_cyb = df_cyb["next_category"].value_counts()
print("\n创业板涨停次日分布:")
print(result1_cyb)

print("\n问题1完成")
