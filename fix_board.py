# -*- coding: utf-8 -*-
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

# 读取股票列表
stocks = pd.read_csv("E:/code/model/raw_data/stock_list.csv")
stocks["symbol"] = stocks["symbol"].astype(str)

print("=" * 60)
print("检查现有分组逻辑问题")
print("=" * 60)

# 检查上海股票
sh_stocks = stocks[stocks["ts_code"].str.endswith(".SH")]
print(f"\n上海股票总数: {len(sh_stocks)}")


# 使用正确的板块分类
def get_board_new(symbol):
    """正确的主板vs创业板/科创板分类"""
    if pd.isna(symbol):
        return "其他"
    if symbol.startswith(("600", "601", "603")):
        return "主板"
    elif symbol.startswith(("000", "001")):  # 主板深圳
        return "主板"
    elif symbol.startswith(("300", "301")):  # 创业板+科创板
        return "创业板/科创板"
    else:
        return "其他"


stocks["board_new"] = stocks["symbol"].apply(get_board_new)
print(f"\n按新逻辑统计:")
print(stocks["board_new"].value_counts())

# 应用到数据
df = pd.read_csv("E:/code/model/process_data/process_data.csv")
df["trade_date"] = df["trade_date"].astype(str)

# 获取symbol
df["symbol"] = df["ts_code"].apply(lambda x: str(x.split(".")[0]))
df["board"] = df["symbol"].apply(get_board_new)

# 重新统计问题1
df_zt = df[df["pct_chg"] >= 9.9].copy()
df_zt["next_close"] = df_zt.groupby("ts_code")["close"].shift(-1)
df_zt["next_pct"] = (
    (df_zt["next_close"] - df_zt["close"]) / df_zt["close"] * 100
).round(4)
df_zt = df_zt.dropna(subset=["next_pct"])

print("\n" + "=" * 60)
print("修正后的涨停次日分布")
print("=" * 60)

for board in ["主板", "创业板/科创板"]:
    df_board = df_zt[df_zt["board"] == board]
    n = len(df_board)
    print(f"\n【{board}】样本数: {n}")

    # 分类
    if board == "主板":

        def classify(x):
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
    else:

        def classify(x):
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
            elif x > -10:
                return "-10~-7%"
            else:
                return "跌停"

    df_board["cat"] = df_board["next_pct"].apply(classify)
    dist = df_board["cat"].value_counts()
    pct = (dist / n * 100).round(2)

    for k, v in pct.items():
        print(f"  {k}: {v}%")

print("\n完成!")
