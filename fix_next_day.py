# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

print("=" * 60)
print("修正'次日'定义：先计算next字段，再筛选事件")
print("=" * 60)

# 读取数据
df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"]).reset_index(drop=True)

# ==================== 问题2: 金叉 ====================
print("\n【问题2: 均线金叉】")
print("-" * 40)

# 先计算均线
df["ma5"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(5).mean())
df["ma10"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(10).mean())
df = df.dropna(subset=["ma5", "ma10"])

# 先计算下一条记录的日期和涨跌幅
df["next_trade_date"] = df.groupby("ts_code")["trade_date"].shift(-1)
df["next_close"] = df.groupby("ts_code")["close"].shift(-1)
df["next_pct"] = df.groupby("ts_code")["pct_chg"].shift(-1)

# 计算金叉 (此时next_pct已经是下一个真实的交易日了)
df["ma5_prev"] = df.groupby("ts_code")["ma5"].shift(1)
df["ma10_prev"] = df.groupby("ts_code")["ma10"].shift(1)
df["golden"] = (df["ma5_prev"] < df["ma10_prev"]) & (df["ma5"] >= df["ma10"])

# 现在按金叉筛选
df_golden = df[df["golden"] == True].copy()
df_golden = df_golden.dropna(subset=["next_pct"])

n2 = len(df_golden)
prob_rise2 = (df_golden["next_pct"] > 0).sum() / n2 * 100
mean2 = df_golden["next_pct"].mean()
std2 = df_golden["next_pct"].std()
se2 = std2 / np.sqrt(n2)
ci_low2 = mean2 - 1.96 * se2
ci_high2 = mean2 + 1.96 * se2

print(f"【修正后】")
print(f"  样本数: {n2}")
print(f"  上涨概率: {prob_rise2:.2f}%")
print(f"  平均涨跌幅: {mean2:.4f}%")
print(f"  95%CI: [{ci_low2:.4f}%, {ci_high2:.4f}%]")

# ==================== 问题3: 金山谷 ====================
print("\n【问题3: 金山谷】")
print("-" * 40)

# 重新读取并计算
df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"]).reset_index(drop=True)

# 计算均线
df["ma5"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(5).mean())
df["ma10"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(10).mean())
df["ma20"] = df.groupby("ts_code")["close"].transform(lambda x: x.rolling(20).mean())
df = df.dropna(subset=["ma5", "ma10", "ma20"])

# 先计算次日数据
df["next_close"] = df.groupby("ts_code")["close"].shift(-1)
df["next_pct"] = df.groupby("ts_code")["pct_chg"].shift(-1)

# 计算金山谷
df["ma5_prev"] = df.groupby("ts_code")["ma5"].shift(1)
df["ma10_prev"] = df.groupby("ts_code")["ma10"].shift(1)
df["ma20_prev"] = df.groupby("ts_code")["ma20"].shift(1)

# 金山谷: MA5上穿MA10和MA20
df["golden_valley"] = (
    (df["ma5_prev"] < df["ma10_prev"])
    & (df["ma5_prev"] < df["ma20_prev"])
    & (df["ma5"] >= df["ma10"])
    & (df["ma5"] >= df["ma20"])
)

# 按金山谷筛选
df_gv = df[df["golden_valley"] == True].copy()
df_gv = df_gv.dropna(subset=["next_pct"])

n3 = len(df_gv)
prob_rise3 = (df_gv["next_pct"] > 0).sum() / n3 * 100
mean3 = df_gv["next_pct"].mean()
std3 = df_gv["next_pct"].std()
se3 = std3 / np.sqrt(n3)
ci_low3 = mean3 - 1.96 * se3
ci_high3 = mean3 + 1.96 * se3

print(f"【修正后】")
print(f"  样本数: {n3}")
print(f"  上涨概率: {prob_rise3:.2f}%")
print(f"  平均涨跌幅: {mean3:.4f}%")
print(f"  95%CI: [{ci_low3:.4f}%, {ci_high3:.4f}%]")

# ==================== 问题4: 封板时间 ====================
print("\n【问题4: 封板时间】")
print("-" * 40)

df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"]).reset_index(drop=True)

# 涨停
df_zt = df[df["pct_chg"] >= 9.9].copy()

# 先计算次日数据
df_zt["next_close"] = df_zt.groupby("ts_code")["close"].shift(-1)
df_zt["next_pct"] = (
    (df_zt["next_close"] - df_zt["close"]) / df_zt["close"] * 100
).round(4)
df_zt = df_zt.dropna(subset=["next_pct"])


# 分类封板类型
def classify_zt(row):
    if row["high"] == row["close"]:
        if row["low"] == row["close"]:
            return "秒封"
        return "早盘封板"
    return "午后/尾盘封板"


df_zt["封板类型"] = df_zt.apply(classify_zt, axis=1)

print(f"【修正后】")
for period in ["秒封", "早盘封板", "午后/尾盘封板"]:
    data = df_zt[df_zt["封板类型"] == period]
    if len(data) > 10:
        n = len(data)
        prob = (data["next_pct"] > 0).sum() / n * 100
        mean = data["next_pct"].mean()
        lb = (data["next_pct"] >= 9.9).sum() / n * 100
        print(
            f"  {period}: 样本={n}, 上涨概率={prob:.2f}%, 平均={mean:.4f}%, 连板={lb:.2f}%"
        )

print("\n" + "=" * 60)
print("修正完成！")
print("=" * 60)
