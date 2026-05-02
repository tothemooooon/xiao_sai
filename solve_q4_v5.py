# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])

# 创建次日日期
df["next_trade_date"] = df.groupby("ts_code")["trade_date"].shift(-1)

# 涨停股票
df_zt = df[df["pct_chg"] >= 9.9].copy()

# 合并次日的收盘价数据
df_merged = df_zt.merge(
    df[["ts_code", "trade_date", "close"]].rename(
        columns={"trade_date": "next_trade_date", "close": "next_close"}
    ),
    on=["ts_code", "next_trade_date"],
    how="left",
)

# 计算次日真实涨跌
df_merged = df_merged.dropna(subset=["next_close", "close"])
df_merged["next_pct"] = (
    (df_merged["next_close"] - df_merged["close"]) / df_merged["close"] * 100
).round(4)

print("次日真实涨跌幅分布:")
print(df_merged["next_pct"].describe())

print("\n次日分类:")
print(f" 继续涨停(>=9.9%): {(df_merged['next_pct'] >= 9.9).sum()}")
print(
    f" 上涨(0-9.9%): {((df_merged['next_pct'] > 0) & (df_merged['next_pct'] < 9.9)).sum()}"
)
print(f" 持平: {(df_merged['next_pct'] == 0).sum()}")
print(f" 下跌(<0): {(df_merged['next_pct'] < 0).sum()}")


# 分类封板时段
def categorize(row):
    if row["high"] == row["close"]:
        if row["low"] == row["close"]:
            return "秒封(开盘即封)"
        else:
            return "早盘封板(9:35-10:30)"
    else:
        return "午后/尾盘封板"


df_merged["封板时段"] = df_merged.apply(categorize, axis=1)

print("\n封板时间各时段分析:")
results = []
for period in ["秒封(开盘即封)", "早盘封板(9:35-10:30)", "午后/尾盘封板"]:
    data = df_merged[df_merged["封板时段"] == period]
    if len(data) > 10:
        n = len(data)

        # 上涨概率
        rising = (data["next_pct"] > 0).sum()
        prob_rise = rising / n * 100

        # 平均涨幅
        mean = data["next_pct"].mean()
        std = data["next_pct"].std()

        # 95%CI
        se = std / np.sqrt(n)
        ci_low = mean - 1.96 * se
        ci_high = mean + 1.96 * se

        # 次日连板
        lb = (data["next_pct"] >= 9.9).sum()
        prob_lb = lb / n * 100

        print(f"\n{period}:")
        print(f"  样本数: {n}")
        print(f"  上涨概率: {prob_rise:.2f}%")
        print(f"  平均涨跌幅: {mean:.4f}%")
        print(f"  标准差: {std:.4f}%")
        print(f"  95%CI: [{ci_low:.4f}%, {ci_high:.4f}%]")
        print(f"  次日连板: {prob_lb:.2f}%")

        results.append(
            {
                "封板时段": period,
                "样本数": n,
                "上涨概率%": round(prob_rise, 2),
                "平均涨跌幅%": round(mean, 4),
                "标准差%": round(std, 4),
                "95%CI下限%": round(ci_low, 4),
                "95%CI上限%": round(ci_high, 4),
                "次日连板概率%": round(prob_lb, 2),
            }
        )

pd.DataFrame(results).to_csv("E:/code/model/process_data/q4_result.csv", index=False)
print("\n已保存到 q4_result.csv")
