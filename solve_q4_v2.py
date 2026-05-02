# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])
df["pct_chg"] = df["pct_chg"].round(4)

df["volatility"] = (df["high"] - df["low"]) / df["close"] * 100
df_zt = df[df["pct_chg"] >= 9.9].copy()


def better_period(vol):
    if vol <= 0.2:
        return "早盘(9:35-10:30)"
    elif vol <= 0.5:
        return "午前(10:30-11:30)"
    elif vol <= 1.0:
        return "午后(13:00-14:30)"
    else:
        return "尾盘(14:30-15:00)"


df_zt["period"] = df_zt["volatility"].apply(better_period)
df_zt["next_pct"] = df_zt.groupby("ts_code")["pct_chg"].shift(-1)
df_zt = df_zt[df_zt["next_pct"].notna()].copy()

print("=" * 60)
print("封板时间分析结果")
print("=" * 60)

results = []
for period in [
    "早盘(9:35-10:30)",
    "午前(10:30-11:30)",
    "午后(13:00-14:30)",
    "尾盘(14:30-15:00)",
]:
    data = df_zt[df_zt["period"] == period]
    if len(data) > 30:
        n = len(data)
        prob_rise = (data["next_pct"] > 0).sum() / n * 100
        mean = data["next_pct"].mean()
        std = data["next_pct"].std()
        se = std / np.sqrt(n)
        ci_low = mean - 1.96 * se
        ci_high = mean + 1.96 * se
        lb = (data["next_pct"] >= 9.9).sum() / n * 100

        results.append(
            {
                "时段": period,
                "样本数": n,
                "上涨概率%": round(prob_rise, 2),
                "平均涨幅%": round(mean, 4),
                "标准差%": round(std, 4),
                "95%CI": f"[{round(ci_low, 4)}%, {round(ci_high, 4)}%]",
                "连板概率%": round(lb, 2),
            }
        )

        print(f"\n{period}:")
        print(f"  样本数: {n}")
        print(f"  上涨概率: {prob_rise:.2f}%")
        print(f"  平均涨幅: {mean:.4f}%")
        print(f"  标准差: {std:.4f}%")
        print(f"  95%CI: [{ci_low:.4f}%, {ci_high:.4f}%]")
        print(f"  次日连板: {lb:.2f}%")

os.makedirs("E:/code/model/process_data", exist_ok=True)
pd.DataFrame(results).to_csv(
    "E:/code/model/process_data/q4_result.csv", index=False, float_format="%.4f"
)
print("\n结果已保存")
