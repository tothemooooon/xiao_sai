# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])
df["pct_chg"] = df["pct_chg"].round(4)

# 涨停
df_zt = df[df["pct_chg"] >= 9.9].copy()


# 判断板块
def get_board(ts_code):
    if (
        ts_code.endswith(".SH")
        or ts_code.startswith("600")
        or ts_code.startswith("601")
        or ts_code.startswith("603")
    ):
        return "主板"
    return "创业板"


df_zt["board"] = df_zt["ts_code"].apply(get_board)
df_zt = df_zt.sort_values(["ts_code", "trade_date"])
df_zt["next_close"] = df_zt.groupby("ts_code")["close"].shift(-1)
df_zt = df_zt.dropna(subset=["next_close"])

# 计算次日涨跌幅
df_zt["next_pct"] = (
    (df_zt["next_close"] - df_zt["close"]) / df_zt["close"] * 100
).round(4)

results = []

# 主板
df_main = df_zt[df_zt["board"] == "主板"]


def classify_main(x):
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
        return "跌停"


df_main["category"] = df_main["next_pct"].apply(classify_main)
q1_main = df_main["category"].value_counts()
t_main = q1_main.sum()
q1_main_pct = (q1_main / t_main * 100).round(4)

order_main = ["涨停", "涨幅>7%", "5~7%", "3~5%", "0~3%", "-3~0%", "-5~-3%", "跌停"]
print("【主板】样本数:", t_main)
for k in order_main:
    if k in q1_main_pct.index:
        print(f"  {k}: {q1_main[k]} ({q1_main_pct[k]}%)")
        results.append(
            {
                "板块": "主板",
                "涨幅区间": k,
                "样本数": int(q1_main[k]),
                "概率(%)": q1_main_pct[k],
            }
        )

# 创业板
df_cyb = df_zt[df_zt["board"] == "创业板"]


def classify_cyb(x):
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
        return "跌停"


df_cyb["category"] = df_cyb["next_pct"].apply(classify_cyb)
q1_cyb = df_cyb["category"].value_counts()
t_cyb = q1_cyb.sum()
q1_cyb_pct = (q1_cyb / t_cyb * 100).round(4)

print("\n【创业板】样本数:", t_cyb)
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
]
for k in order_cyb:
    if k in q1_cyb_pct.index:
        print(f"  {k}: {q1_cyb[k]} ({q1_cyb_pct[k]}%)")
        results.append(
            {
                "板块": "创业板",
                "涨幅区间": k,
                "样本数": int(q1_cyb[k]),
                "概率(%)": q1_cyb_pct[k],
            }
        )

pd.DataFrame(results).to_csv("E:/code/model/process_data/q1_result.csv", index=False)
print("\n已保存")
