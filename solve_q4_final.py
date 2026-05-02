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


# 分类封板类型
def categorize(row):
    if row["high"] == row["close"]:  # 最高价=收盘价
        if row["low"] == row["close"]:
            return "秒封(开盘即封)"
        else:
            return "早盘封板(9:35-10:30)"
    else:
        # 检查接近收盘的波动
        return "午后封板(13:00-15:00)"


df_zt["封板时段"] = df_zt.apply(categorize, axis=1)

# 获取次日涨跌幅
df_zt["next_pct"] = df_zt.groupby("ts_code")["pct_chg"].shift(-1)
df_zt = df_zt[df_zt["next_pct"].notna()].copy()

print("=" * 60)
print("封板时间分析结果")
print("=" * 60)

# 按题目要求的四个时间段
# 注意：由于使用日K数据，我们只能近似分类

results = []
for period in ["秒封(开盘即封)", "早盘封板(9:35-10:30)", "午后封板(13:00-15:00)"]:
    data = df_zt[df_zt["封板时段"] == period]
    if len(data) > 10:
        n = len(data)

        # 上涨概率: 次日涨幅>0 (注意这是相对于前一日收盘)
        rising = (data["next_pct"] > 0).sum()
        prob_rise = rising / n * 100

        # 平均涨幅
        mean = data["next_pct"].mean()
        std = data["next_pct"].std()

        # 95%置信区间
        se = std / np.sqrt(n)
        ci_low = mean - 1.96 * se
        ci_high = mean + 1.96 * se

        # 次日连板(再次涨停)
        lb = (data["next_pct"] >= 9.9).sum()
        prob_lb = lb / n * 100

        print(f"\n{period}:")
        print(f"  样本数: {n}")
        print(f"  上涨概率: {prob_rise:.2f}%")
        print(f"  平均涨跌幅: {mean:.4f}%")
        print(f"  标准差: {std:.4f}%")
        print(f"  95%CI: [{ci_low:.4f}%, {ci_high:.4f}%]")
        print(f"  次日连板数: {lb} ({prob_lb:.2f}%)")

        results.append(
            {
                "封板时段": period,
                "样本数": n,
                "上涨概率(%)": round(prob_rise, 2),
                "平均涨跌幅(%)": round(mean, 4),
                "标准差(%)": round(std, 4),
                "95%CI下限(%)": round(ci_low, 4),
                "95%CI上限(%)": round(ci_high, 4),
                "次日连板概率(%)": round(prob_lb, 2),
            }
        )

# 保存
pd.DataFrame(results).to_csv(
    "E:/code/model/process_data/q4_result.csv", index=False, float_format="%.4f"
)
print("\n结果已保存")
