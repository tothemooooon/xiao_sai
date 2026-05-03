# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])

# 原始涨跌幅
df["pct_chg"] = df["pct_chg"].round(4)

# 识别涨停股票
df["is_zt"] = df["pct_chg"] >= 9.9
df_zt = df[df["is_zt"] == True].copy()


# 判断板块类型
def get_board(ts_code):
    if (
        ts_code.endswith(".SH")
        or ts_code.startswith("600")
        or ts_code.startswith("601")
        or ts_code.startswith("603")
    ):
        return "主板"
    else:
        return "创业板"


df_zt["board"] = df_zt["ts_code"].apply(get_board)

# 排序并获取次日数据
df_zt = df_zt.sort_values(["ts_code", "trade_date"])
df_zt["next_trade_date"] = df_zt.groupby("ts_code")["trade_date"].shift(-1)
df_zt["next_close"] = df_zt.groupby("ts_code")["close"].shift(-1)
df_zt["next_pct_chg"] = df_zt.groupby("ts_code")["pct_chg"].shift(-1)

# 过滤无效数据
df_zt = df_zt.dropna(subset=["next_close", "next_pct_chg"])

print("=" * 60)
print("问题1: 涨停次日走势分析")
print("=" * 60)

# 主板
df_main = df_zt[df_zt["board"] == "主板"].copy()
df_main["next_pct"] = (
    (df_main["next_close"] - df_main["close"]) / df_main["close"] * 100
).round(4)


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
    elif x > -10:
        return "-7~-5%"
    elif x >= -9.9:
        return "-7~-5%"
    else:
        return "跌停"


df_main["category"] = df_main["next_pct"].apply(classify_main)
q1_main = df_main["category"].value_counts()
total_main = q1_main.sum()
q1_main_pct = (q1_main / total_main * 100).round(4)

print("\n【主板涨停次日分布】")
print("-" * 60)
print(f"{'涨幅区间':<20} {'样本数':>12} {'概率(%)':>12}")
print("-" * 60)
order_main = [
    "涨停",
    "涨幅>7%",
    "5~7%",
    "3~5%",
    "0~3%",
    "-3~0%",
    "-5~-3%",
    "-7~-5%",
    "跌停",
    "无数据",
]
for k in order_main:
    if k in q1_main_pct.index:
        print(f"{k:<20} {q1_main[k]:>12} {q1_main_pct[k]:>12.2f}")
print("-" * 60)
print(f"{'合计':<20} {total_main:>12} {'100.00':>12}")

# 创业板
df_cyb = df_zt[df_zt["board"] == "创业板"].copy()
df_cyb["next_pct"] = (
    (df_cyb["next_close"] - df_cyb["close"]) / df_cyb["close"] * 100
).round(4)


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


df_cyb["category"] = df_cyb["next_pct"].apply(classify_cyb)
q1_cyb = df_cyb["category"].value_counts()
total_cyb = q1_cyb.sum()
q1_cyb_pct = (q1_cyb / total_cyb * 100).round(4)

print("\n" + "=" * 60)
print("【创业板涨停次日分布】")
print("-" * 60)
print(f"{'涨幅区间':<20} {'样本数':>12} {'概率(%)':>12}")
print("-" * 60)
order_cyb = [
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
    "跌停",
    "无数据",
]
for k in order_cyb:
    if k in q1_cyb_pct.index:
        print(f"{k:<20} {q1_cyb[k]:>12} {q1_cyb_pct[k]:>12.2f}")
print("-" * 60)
print(f"{'合计':<20} {total_cyb:>12} {'100.00':>12}")

# 保存结果
results = []
for k in order_main:
    if k in q1_main_pct.index:
        results.append(
            {
                "板块": "主板",
                "涨幅区间": k,
                "样本数": int(q1_main[k]),
                "概率(%)": round(q1_main_pct[k], 4),
            }
        )
for k in order_cyb:
    if k in q1_cyb_pct.index:
        results.append(
            {
                "板块": "创业板",
                "涨幅区间": k,
                "样本数": int(q1_cyb[k]),
                "概率(%)": round(q1_cyb_pct[k], 4),
            }
        )

pd.DataFrame(results).to_csv("E:/code/model/process_data/q1_result.csv", index=False)
print("\n结果已保存到 q1_result.csv")
