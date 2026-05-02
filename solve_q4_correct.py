# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)
df = df.sort_values(["ts_code", "trade_date"])

# 理解数据: pct_chg是当日相对于前一日收盘价的涨跌幅
# 涨停后次日的收益应该是：
# (第2日收盘价 - 第1日收盘价) / 第1日收盘价 * 100

# 正确做法: 需要从原始数据中获取次日真实涨跌幅
# 用shift(-1)获取次日的pct_chg

df["pct_chg"] = df["pct_chg"].round(4)

# 涨停股票
df_zt = df[df["pct_chg"] >= 9.9].copy()
df_zt["next_day_pct"] = df_zt.groupby("ts_code")["pct_chg"].shift(
    -1
)  # 这是次日的涨跌幅
df_zt = df_zt.dropna(subset=["next_day_pct"])

print("次日涨跌幅分布:")
print(df_zt["next_day_pct"].describe())

print("\n次日分类:")
print(f" 继续涨停: {(df_zt['next_day_pct'] >= 9.9).sum()}")
print(f" 上涨: {((df_zt['next_day_pct'] > 0) & (df_zt['next_day_pct'] < 9.9)).sum()}")
print(f" 下跌: {(df_zt['next_day_pct'] < 0).sum()}")


# 分类封板时间
def categorize(row):
    if row["high"] == row["close"]:
        if row["low"] == row["close"]:
            return "秒封(开盘即封)"
        else:
            return "早盘封板(9:35-10:30)"
    else:
        return "午后封板(13:00-15:00)"


df_zt["封板时段"] = df_zt.apply(categorize, axis=1)

print("\n封板时间各时段分析:")
results = []
for period in ["秒封(开盘即封)", "早盘封板(9:35-10:30)", "午后封板(13:00-15:00)"]:
    data = df_zt[df_zt["封板时段"] == period]
    if len(data) > 10:
        n = len(data)

        # 上涨概率(次日涨幅>0)
        rising = (data["next_day_pct"] > 0).sum()
        prob_rise = rising / n * 100

        # 平均涨幅
        mean = data["next_day_pct"].mean()
        std = data["next_day_pct"].std()

        # 95%CI
        se = std / np.sqrt(n)
        ci_low = mean - 1.96 * se
        ci_high = mean + 1.96 * se

        # 次日连板
        lb = (data["next_day_pct"] >= 9.9).sum()
        prob_lb = lb / n * 100

        print(f"\n{period}:")
        print(f"  样本数: {n}")
        print(f"  上涨概率: {prob_rise:.2f}%")
        print(f"  平均涨跌幅: {mean:.4f}%")
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
print("\n已保存")
