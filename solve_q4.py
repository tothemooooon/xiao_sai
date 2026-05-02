# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

os.makedirs("E:/code/model/process_data", exist_ok=True)

print("分析封板时间...")
df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])

# 原始pct_chg是当日涨跌幅
df["pct_chg"] = df["pct_chg"].round(4)

# 日内波动
df["volatility"] = (df["high"] - df["low"]) / df["close"] * 100

# 识别涨停股
df_zt = df[df["pct_chg"] >= 9.9].copy()
print(f"涨停记录: {len(df_zt)}")

# 计算次日涨跌幅(不是次日涨幅，是第2日的涨跌幅)
# shift(-1)是次日，但我们需要再下一天
df_zt["next2_pct"] = df_zt.groupby("ts_code")["pct_chg"].shift(-2)
df_zt["next_pct"] = df_zt.groupby("ts_code")["pct_chg"].shift(-1)


# 波动判断封板时间
def guess_period(vol):
    if vol < 0.3:
        return "早盘"
    elif vol < 0.8:
        return "午前"
    elif vol < 1.5:
        return "午后"
    else:
        return "尾盘"


df_zt["period_guess"] = df_zt["volatility"].apply(guess_period)

# 统计分布
print("\n封板时间分布:")
period_dist = df_zt["period_guess"].value_counts()
print(period_dist)

# 过滤无效数据
df_zt = df_zt[df_zt["next_pct"].notna()].copy()

print(f"\n有效次日数据: {len(df_zt)}")

# 分析各时段
results = []
for period in ["早盘", "午前", "午后", "尾盘"]:
    subset = df_zt[df_zt["period_guess"] == period]
    if len(subset) >= 10:
        n = len(subset)

        # 上涨概率(次日涨幅>0)
        rising = (subset["next_pct"] > 0).sum()
        prob_rise = rising / n * 100

        # 平均涨幅
        mean_pct = subset["next_pct"].mean()
        std_pct = subset["next_pct"].std()

        # 置信区间
        se = std_pct / np.sqrt(n)
        ci_low = mean_pct - 1.96 * se
        ci_high = mean_pct + 1.96 * se

        # 次日继续涨停/连板概率
        rebound = (subset["next_pct"] >= 9.9).sum()
        prob_lb = rebound / n * 100

        print(f"\n【{period}】")
        print(f"  样本数: {n}")
        print(f"  上涨概率: {prob_rise:.2f}%")
        print(f"  平均涨幅: {mean_pct:.4f}%")
        print(f"  95%CI: [{ci_low:.4f}%, {ci_high:.4f}%]")
        print(f"  次日连板: {prob_lb:.2f}%")

        results.append(
            {
                "时段": period,
                "样本数": n,
                "上涨概率": round(prob_rise, 2),
                "平均涨幅(%)": round(mean_pct, 4),
                "标准差(%)": round(std_pct, 4),
                "95%CI下限(%)": round(ci_low, 4),
                "95%CI上限(%)": round(ci_high, 4),
                "次日连板概率(%)": round(prob_lb, 2),
            }
        )

# 保存
result_df = pd.DataFrame(results)
result_df.to_csv(
    "E:/code/model/process_data/q4_result.csv", index=False, float_format="%.4f"
)
print("\n结果已保存")

# 保存详细数据
df_zt.to_csv("E:/code/model/process_data/zt_with_period.csv", index=False)
print("详细数据已保存")
