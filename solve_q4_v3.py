# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])
df["pct_chg"] = df["pct_chg"].round(4)

# 涨停股
df_zt = df[df["pct_chg"] >= 9.9].copy()

# 如果最高价==收盘价，说明早盘就封板且未打开
# 如果最高价>收盘价，说明有打开过

df_zt["is_zt_always"] = df_zt["high"] == df_zt["close"]  # 一直封板


# 分类
def categorize(row):
    if row["high"] == row["close"]:
        if row["low"] == row["close"]:
            return "秒封(早盘)"  # 一字涨停/开盘即封
        else:
            return "早盘封板"
    else:
        return "盘中/尾盘封板"


df_zt["zt_type"] = df_zt.apply(categorize, axis=1)
df_zt["next_pct"] = df_zt.groupby("ts_code")["pct_chg"].shift(-1)
df_zt = df_zt[df_zt["next_pct"].notna()].copy()

print("=" * 60)
print("封板时间分析结果")
print("=" * 60)

results = []
for period in ["秒封(早盘)", "早盘封板", "盘中/尾盘封板"]:
    data = df_zt[df_zt["zt_type"] == period]
    if len(data) > 10:
        n = len(data)
        prob_rise = (data["next_pct"] > 0).sum() / n * 100
        mean = data["next_pct"].mean()
        std = data["next_pct"].std()
        se = std / np.sqrt(n)
        ci_low = mean - 1.96 * se
        ci_high = mean + 1.96 * se
        lb = (data["next_pct"] >= 9.9).sum() / n * 100

        print(f"\n{period}:")
        print(f"  样本数: {n}")
        print(f"  上涨概率: {prob_rise:.2f}%")
        print(f"  平均涨幅: {mean:.4f}%")
        print(f"  95%CI: [{ci_low:.4f}%, {ci_high:.4f}%]")
        print(f"  次日连板: {lb:.2f}%")

        results.append(
            {
                "封板时段": period,
                "样本数": n,
                "上涨概率%": round(prob_rise, 2),
                "平均涨幅%": round(mean, 4),
                "95%CI下限%": round(ci_low, 4),
                "95%CI上限%": round(ci_high, 4),
                "次日连板概率%": round(lb, 2),
            }
        )

os.makedirs("E:/code/model/process_data", exist_ok=True)
pd.DataFrame(results).to_csv(
    "E:/code/model/process_data/q4_result.csv", index=False, float_format="%.4f"
)
print("\n结果已保存")
