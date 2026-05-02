# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

os.makedirs("E:/code/model/results", exist_ok=True)

print("读取数据...")
df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"]).reset_index(drop=True)

print(f"数据: {len(df)}行")

df["pct_chg_calc"] = ((df["close"] - df["pre_close"]) / df["pre_close"] * 100).round(4)

# ========== 问题1: 涨停 ==========
print("\n" + "=" * 60)
print("问题1: 涨停次日走势分布")
print("=" * 60)


# 主板识别
def is_main(ts_code):
    return (
        ts_code.endswith(".SH")
        or ts_code.startswith("600")
        or ts_code.startswith("601")
        or ts_code.startswith("603")
    )


df["is_main"] = df["ts_code"].apply(is_main)
df_main = df[df["is_main"] == True]
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
    else:
        return "<-5%"


df_main_zting["category"] = df_main_zting["next_pct_chg"].apply(classify_main)
q1_main = df_main_zting["category"].value_counts()
total_main = q1_main.sum()
q1_main_pct = (q1_main / total_main * 100).round(4)

print("\n【主板涨停次日分布】")
for k in ["涨停", "涨幅>7%", "5~7%", "3~5%", "0~3%", "-3~0%", "-5~-3%", "<-5%"]:
    if k in q1_main_pct.index:
        print(f"  {k}: {q1_main_pct[k]:.2f}%")
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
    else:
        return "<-10%"


df_cyb_zting["category"] = df_cyb_zting["next_pct_chg"].apply(classify_cyb)
q1_cyb = df_cyb_zting["category"].value_counts()
total_cyb = q1_cyb.sum()
q1_cyb_pct = (q1_cyb / total_cyb * 100).round(4)

print("\n【创业板涨停次日分布】")
for k in [
    "涨停",
    "涨幅>10%",
    "7~10%",
    "5~7%",
    "3~5%",
    "0~3%",
    "-3~0%",
    "-5~-3%",
    "-7~-5%",
    "-10~-7%",
    "<-10%",
]:
    if k in q1_cyb_pct.index:
        print(f"  {k}: {q1_cyb_pct[k]:.2f}%")
print(f"样本数: {total_cyb}")

# ========== 问题2: 金叉 ==========
print("\n" + "=" * 60)
print("问题2: 金叉买入")
print("=" * 60)

# 计算均线
print("计算均线...")
df = df.sort_values(["ts_code", "trade_date"])
df["ma5"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(5).mean())
df["ma10"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(10).mean())

df = df.dropna(subset=["ma5", "ma10"])
df["ma5_prev"] = df.groupby("ts_code")["ma5"].shift(1)
df["ma10_prev"] = df.groupby("ts_code")["ma10"].shift(1)

# 金叉
df["golden"] = (df["ma5_prev"] < df["ma10_prev"]) & (df["ma5"] >= df["ma10"])
df_golden = df[df["golden"] == True].copy()
df_golden["next_pct_chg"] = df_golden.groupby("ts_code")["pct_chg_calc"].shift(-1)
df_golden = df_golden.dropna(subset=["next_pct_chg"])

if len(df_golden) > 0:
    n2 = len(df_golden)
    rising = (df_golden["next_pct_chg"] > 0).sum()
    prob_rise = rising / n2 * 100
    mean_pct = df_golden["next_pct_chg"].mean()
    std_pct = df_golden["next_pct_chg"].std()
    se = std_pct / np.sqrt(n2)
    ci_low = mean_pct - 1.96 * se
    ci_high = mean_pct + 1.96 * se

    print(f"\n【金叉后次日收益】")
    print(f"样本数: {n2}")
    print(f"上涨概率: {prob_rise:.2f}%")
    print(f"平均涨跌幅: {mean_pct:.4f}%")
    print(f"标准差: {std_pct:.4f}%")
    print(f"95%置信区间: [{ci_low:.4f}%, {ci_high:.4f}%]")

# ========== 问题3: 金山谷 ==========
print("\n" + "=" * 60)
print("问题3: 金山谷买入")
print("=" * 60)

df["ma5"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(5).mean())
df["ma10"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(10).mean())
df["ma20"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(20).mean())

df = df.dropna(subset=["ma5", "ma10", "ma20"])
df["ma5_prev"] = df.groupby("ts_code")["ma5"].shift(1)
df["ma10_prev"] = df.groupby("ts_code")["ma10"].shift(1)
df["ma20_prev"] = df.groupby("ts_code")["ma20"].shift(1)

# 金山谷
df["golden_valley"] = (
    (df["ma5_prev"] < df["ma10_prev"])
    & (df["ma5_prev"] < df["ma20_prev"])
    & (df["ma5"] >= df["ma10"])
    & (df["ma5"] >= df["ma20"])
)

df_gv = df[df["golden_valley"] == True].copy()
df_gv["future_10"] = df_gv.groupby("ts_code")["pct_chg_calc"].shift(-10)
df_gv = df_gv.dropna(subset=["future_10"])

if len(df_gv) > 0:
    n3 = len(df_gv)
    rising = (df_gv["future_10"] > 0).sum()
    prob_rise = rising / n3 * 100
    mean_pct = df_gv["future_10"].mean()
    std_pct = df_gv["future_10"].std()
    se = std_pct / np.sqrt(n3)
    ci_low = mean_pct - 1.96 * se
    ci_high = mean_pct + 1.96 * se

    print(f"\n【金山谷后10日收益】")
    print(f"样本数: {n3}")
    print(f"上涨概率: {prob_rise:.2f}%")
    print(f"平均涨跌幅: {mean_pct:.4f}%")
    print(f"标准差: {std_pct:.4f}%")
    print(f"95%置信区间: [{ci_low:.4f}%, {ci_high:.4f}%]")

# ========== 问题4 ==========
print("\n" + "=" * 60)
print("问题4: 封板时间")
print("=" * 60)
print("\n需要分时数据，当前日交易数据无法分析")

print("\n完成!")
