# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"]).reset_index(drop=True)
df["pct_chg_calc"] = ((df["close"] - df["pre_close"]) / df["pre_close"] * 100).round(4)

# 金山谷
df["ma5"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(5).mean())
df["ma10"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(10).mean())
df["ma20"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(20).mean())
df = df.dropna(subset=["ma5", "ma10", "ma20"])
df["ma5_prev"] = df.groupby("ts_code")["ma5"].shift(1)
df["ma10_prev"] = df.groupby("ts_code")["ma10"].shift(1)
df["ma20_prev"] = df.groupby("ts_code")["ma20"].shift(1)

df["golden_valley"] = (
    (df["ma5_prev"] < df["ma10_prev"])
    & (df["ma5_prev"] < df["ma20_prev"])
    & (df["ma5"] >= df["ma10"])
    & (df["ma5"] >= df["ma20"])
)

print(f"金山谷数量: {df['golden_valley'].sum()}")

df_gv = df[df["golden_valley"] == True].copy()
if len(df_gv) > 0:
    # 使用次日数据分析（更多样本）
    df_gv["next_pct"] = df_gv.groupby("ts_code")["pct_chg_calc"].shift(-1)
    df_gv = df_gv.dropna(subset=["next_pct"])
    print(f"次日数据: {len(df_gv)}")

    n3 = len(df_gv)
    rising = (df_gv["next_pct"] > 0).sum()
    prob_rise = rising / n3 * 100
    mean_pct = df_gv["next_pct"].mean()
    std_pct = df_gv["next_pct"].std()
    se = std_pct / np.sqrt(n3)
    ci_low = mean_pct - 1.96 * se
    ci_high = mean_pct + 1.96 * se

    print(f"上涨概率: {prob_rise:.2f}%")
    print(f"平均涨跌幅: {mean_pct:.4f}%")
    print(f"标准差: {std_pct:.4f}%")
    print(f"95%置信区间: [{ci_low:.4f}%, {ci_high:.4f}%]")

    # 再用3日试试
    df_gv["future_3"] = df_gv.groupby("ts_code")["pct_chg_calc"].shift(-3)
    df_gv3 = df_gv.dropna(subset=["future_3"])
    if len(df_gv3) > 0:
        n3 = len(df_gv3)
        rising3 = (df_gv3["future_3"] > 0).sum()
        prob_rise3 = rising3 / n3 * 100
        mean_pct3 = df_gv3["future_3"].mean()
        std_pct3 = df_gv3["future_3"].std()
        se3 = std_pct3 / np.sqrt(n3)
        ci_low3 = mean_pct3 - 1.96 * se3
        ci_high3 = mean_pct3 + 1.96 * se3

        print(f"\n3日数据: {n3}")
        print(f"上涨概率: {prob_rise3:.2f}%")
        print(f"平均涨跌幅: {mean_pct3:.4f}%")
        print(f"95%置信区间: [{ci_low3:.4f}%, {ci_high3:.4f}%]")
