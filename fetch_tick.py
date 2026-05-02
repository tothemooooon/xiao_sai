# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd
import os

os.makedirs("E:/code/model/raw_data", exist_ok=True)

lg = bs.login()
print("登录成功")

# 获取交易日列表
from datetime import datetime, timedelta
import time

start_date = "2025-05-06"
end_date = "2026-04-30"

# 需要分析的股票(从日交易数据中筛选涨停的)
print("读取日交易数据...")
daily = pd.read_csv("E:/code/model/process_data/process_data.csv")
daily["pct_chg"] = daily["pct_chg"].round(4)

# 筛选涨停股票
zt_stocks = daily[daily["pct_chg"] >= 9.9][["ts_code", "trade_date"]].drop_duplicates()
print(f"涨停股票记录: {len(zt_stocks)}")


# 获取分时数据并识别封板时间
# 转换为baostock格式
def ts_to_bs(ts_code):
    if ts_code.endswith(".SH"):
        return "sh." + ts_code.replace(".SH", "")
    else:
        return "sz." + ts_code.replace(".SZ", "")


# 只分析近期数据(2025年5-6月)
sample_dates = [
    "20250506",
    "20250507",
    "20250508",
    "20250509",
    "20250512",
    "20250513",
    "20250514",
    "20250515",
    "20250516",
    "20250519",
]

all_zting = []
sample_stocks = zt_stocks[zt_stocks["trade_date"].isin(sample_dates)]

print(f"需要分析的涨停记录: {len(sample_stocks)}")

# 批量获取分时数据
unique_stocks = sample_stocks["ts_code"].unique()[:200]  # 取200只

for i, code in enumerate(unique_stocks):
    bs_code = ts_to_bs(code)
    try:
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,time,open,high,low,close,volume",
            start_date="20250506",
            end_date="20250520",
            frequency="5",
            adjustflag="2",
        )

        data_list = []
        while rs.error_code == "0" and rs.next():
            data_list.append(rs.get_row_data())

        if data_list:
            df = pd.DataFrame(data_list, columns=rs.fields)

            # 识别封板(开盘价=最高价=收盘价 且涨幅>=9.9%)
            if len(df) > 0:
                df["close"] = df["close"].astype(float)
                df["open"] = df["open"].astype(float)
                df["high"] = df["high"].astype(float)

                # 计算当日收盘涨幅(相对于开盘)
                last_row = df.iloc[-1]
                first_row = df.iloc[0]
                if first_row["open"] != "0":
                    pct = (
                        (float(last_row["close"]) - float(first_row["open"]))
                        / float(first_row["open"])
                        * 100
                    )

                    if pct >= 9.9:  # 涨停
                        # 提取时间
                        time_str = str(df.iloc[0]["time"])
                        hour = int(time_str[8:10])
                        minute = int(time_str[10:12])

                        # 判断封板时段
                        if hour == 9 and minute >= 35 or (hour == 10 and minute < 30):
                            period = "早盘(9:35-10:30)"
                        elif (
                            hour == 10 and minute >= 30 or (hour == 11 and minute < 30)
                        ):
                            period = "午前(10:30-11:30)"
                        elif hour == 13 or (hour == 14 and minute < 30):
                            period = "午后(13:00-14:30)"
                        elif hour == 14 and minute >= 30:
                            period = "尾盘(14:30-15:00)"
                        else:
                            period = "其他"

                        all_zting.append(
                            {
                                "ts_code": code,
                                "date": str(df.iloc[0]["date"]),
                                "period": period,
                                "time": time_str,
                            }
                        )
    except Exception as e:
        pass

    if (i + 1) % 50 == 0:
        print(f"进度: {i + 1}/{len(unique_stocks)}")
    time.sleep(0.1)

bs.logout()

if all_zting:
    result_df = pd.DataFrame(all_zting)
    result_df.to_csv("E:/code/model/raw_data/zt_period.csv", index=False)
    print(f"\n封板数据已保存: {len(result_df)}条")
    print(result_df["period"].value_counts())
else:
    print("未获取到封板数据")
