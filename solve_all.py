# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

os.makedirs("E:/code/model/results", exist_ok=True)

print("读取数据...")
df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])

print(f"数据总量: {len(df)}")
print(f"日期范围: {df['trade_date'].min()} - {df['trade_date'].max()}")

df["pct_chg_calc"] = ((df["close"] - df["pre_close"]) / df["pre_close"] * 100).round(4)

# ========== 问题1: 涨停 ==========
print("\n" + "=" * 60)
print("问题1: 涨停次日走势分析")
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

# ========== 问题2: 金叉 ==========
print("\n" + "=" * 60)
print("问题2: 均线金叉分析")
print("=" * 60)

df2 = df.copy()
df2 = df2.sort_values(["ts_code", "trade_date"])
df2["ma5"] = df2.groupby("ts_code")["close"].rolling(5).mean().reset_index(level=0)
df2["ma10"] = df2.groupby("ts_code")["close"].rolling(10).mean().reset_index(level=0)

df2 = df2.dropna(subset=["ma5", "ma10"])
df2["ma5_prev"] = df2.groupby("ts_code")["ma5"].shift(1)
df2["ma10_prev"] = df2.groupby("ts_code")["ma10"].shift(1)
df2["golden"] = (df2["ma5_prev"] < df2["ma10_prev"]) & (df2["ma5"] >= df2["ma10"])

df2_golden = df2[df2["golden"] == True].copy()
df2_golden["next_pct_chg"] = df2_golden.groupby("ts_code")["pct_chg_calc"].shift(-1)
df2_golden = df2_golden.dropna(subset=["next_pct_chg"])

if len(df2_golden) > 0:
    rising = df2_golden[df2_golden["next_pct_chg"] > 0]
    prob_rise = len(rising) / len(df2_golden) * 100
    mean_pct = df2_golden["next_pct_chg"].mean()
    std_pct = df2_golden["next_pct_chg"].std()
    n = len(df2_golden)
    se = std_pct / np.sqrt(n)
    ci_low = mean_pct - 1.96 * se
    ci_high = mean_pct + 1.96 * se

    print(f"\n金叉样本数: {n}")
    print(f"上涨概率: {prob_rise:.2f}%")
    print(f"平均涨跌幅: {mean_pct:.4f}%")
    print(f"标准差: {std_pct:.4f}%")
    print(f"95%置信区间: [{ci_low:.4f}%, {ci_high:.4f}%]")

# ========== 问题3: 金山谷 ==========
print("\n" + "=" * 60)
print("问题3: 金山谷分析")
print("=" * 60)

df3 = df.copy()
df3 = df3.sort_values(["ts_code", "trade_date"])
df3["ma5"] = df3.groupby("ts_code")["close"].rolling(5).mean().reset_index(level=0)
df3["ma10"] = df3.groupby("ts_code")["close"].rolling(10).mean().reset_index(level=0)
df3["ma20"] = df3.groupby("ts_code")["close"].rolling(20).mean().reset_index(level=0)

df3 = df3.dropna(subset=["ma5", "ma10", "ma20"])
df3["ma5_prev"] = df3.groupby("ts_code")["ma5"].shift(1)
df3["ma10_prev"] = df3.groupby("ts_code")["ma10"].shift(1)
df3["ma20_prev"] = df3.groupby("ts_code")["ma20"].shift(1)

# 金山谷：ma5上穿ma10和ma20
df3["golden"] = (
    (df3["ma5_prev"] < df3["ma10_prev"])
    & (df3["ma5_prev"] < df3["ma20_prev"])
    & (df3["ma5"] >= df3["ma10"])
    & (df3["ma5"] >= df3["ma20"])
)

df3_golden = df3[df3["golden"] == True].copy()

if len(df3_golden) > 0:
    # 10日涨跌幅
    df3_golden["future_10_pct"] = df3_golden.groupby("ts_code")["pct_chg_calc"].shift(
        -10
    )
    df3_golden = df3_golden.dropna(subset=["future_10_pct"])

    if len(df3_golden) > 0:
        rising_gv = df3_golden[df3_golden["future_10_pct"] > 0]
        prob_rise_gv = len(rising_gv) / len(df3_golden) * 100
        mean_pct_gv = df3_golden["future_10_pct"].mean()
        std_pct_gv = df3_golden["future_10_pct"].std()
        n_gv = len(df3_golden)
        se_gv = std_pct_gv / np.sqrt(n_gv)
        ci_low_gv = mean_pct_gv - 1.96 * se_gv
        ci_high_gv = mean_pct_gv + 1.96 * se_gv

        print(f"\n金山谷样本数: {n_gv}")
        print(f"10日内上涨概率: {prob_rise_gv:.2f}%")
        print(f"10日平均涨跌幅: {mean_pct_gv:.4f}%")
        print(f"标准差: {std_pct_gv:.4f}%")
        print(f"95%置信区间: [{ci_low_gv:.4f}%, {ci_high_gv:.4f}%]")

print("\n" + "=" * 60)
print("问题4: 封板时间")
print("=" * 60)
print("\n注意: 当前数据为日交易数据，无分时数据")
print("需额外获取分时数据才能分析封板时间")

print("\n计算完成!")
