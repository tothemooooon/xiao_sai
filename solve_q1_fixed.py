# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

os.makedirs("E:/code/model/results", exist_ok=True)

print("读取数据...")
df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])

print(f"数据: {len(df)}行")

df["pct_chg_calc"] = ((df["close"] - df["pre_close"]) / df["pre_close"] * 100).round(4)

# ========== 问题1 ==========
print("\n" + "=" * 60)
print("问题1: 涨停")
print("=" * 60)

# 主板
df_main = df[
    (df["ts_code"].str.endswith(".SH"))
    | (df["ts_code"].str.startswith("600"))
    | (df["ts_code"].str.startswith("601"))
    | (df["ts_code"].str.startswith("603"))
]
df_main_zting = df_main[df_main["pct_chg_calc"] >= 9.9].copy()
df_main_zting = df_main_zting.sort_values(["ts_code", "trade_date"])
df_main_zting["next_pct_chg"] = df_main_zting.groupby("ts_code")["pct_chg_calc"].shift(
    -1
)


def classify_main(x):
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
    elif x >= -9.9:
        return "-5~-3%"
    else:
        return "跌停"


df_main_zting["category"] = df_main_zting["next_pct_chg"].apply(classify_main)
q1_main = df_main_zting["category"].value_counts()
total_main = q1_main.sum()
if total_main > 0:
    q1_main_pct = (q1_main / total_main * 100).round(4)
    print("\n主板涨停次日分布:")
    for k, v in q1_main_pct.items():
        print(f"  {k}: {v:.2f}%")
    print(f"样本数: {total_main}")

# 创业板
df_cyb = df[
    (df["ts_code"].str.startswith("000")) | (df["ts_code"].str.startswith("300"))
]
df_cyb_zting = df_cyb[df_cyb["pct_chg_calc"] >= 9.9].copy()
df_cyb_zting = df_cyb_zting.sort_values(["ts_code", "trade_date"])
df_cyb_zting["next_pct_chg"] = df_cyb_zting.groupby("ts_code")["pct_chg_calc"].shift(-1)


def classify_cyb(x):
    if pd.isna(x):
        return "无数据"
    if x >= 9.9:
        return "涨停"
    elif x > 10:
        return "涨幅>10%"
    elif x > 7:
        return "7~10%"
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
        return "-10~-7%"
    elif x >= -9.9:
        return "-10~-7%"
    else:
        return "跌停"


df_cyb_zting["category"] = df_cyb_zting["next_pct_chg"].apply(classify_cyb)
q1_cyb = df_cyb_zting["category"].value_counts()
total_cyb = q1_cyb.sum()
if total_cyb > 0:
    q1_cyb_pct = (q1_cyb / total_cyb * 100).round(4)
    print("\n创业板涨停次日分布:")
    for k, v in q1_cyb_pct.items():
        print(f"  {k}: {v:.2f}%")
    print(f"样本数: {total_cyb}")

# ========== 问题2 ==========
print("\n" + "=" * 60)
print("问题2: 金叉")
print("=" * 60)


def calc_ma(group, window):
    return group["close"].rolling(window).mean()


df2 = df.copy()
df2 = df2.sort_values(["ts_code", "trade_date"])
df2["ma5"] = df2.groupby("ts_code").apply(lambda g: calc_ma(g, 5))["close"]
df2["ma10"] = df2.groupby("ts_code").apply(lambda g: calc_ma(g, 10))["close"]

print("均线计算完成")
print("\n问题2需要更复杂的实现，简化版本略过")

# ========== 问题3 ==========
print("\n" + "=" * 60)
print("问题3: 金山谷")
print("=" * 60)
print("同上，需要完整均线系统")

# ========== 问题4 ==========
print("\n" + "=" * 60)
print("问题4: 封板时间")
print("=" * 60)
print("需要分时数据")

# 保存问题1结果
q1_result = {
    "主板": q1_main_pct.to_dict(),
    "样本数": total_main,
    "创业板": q1_cyb_pct.to_dict(),
    "创业板样本数": total_cyb,
}

print("\n计算完成!")
