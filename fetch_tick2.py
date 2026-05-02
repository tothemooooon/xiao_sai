# -*- coding: utf-8 -*-
import baostock as bs
import pandas as pd
import os
import time

os.makedirs("E:/code/model/raw_data", exist_ok=True)

lg = bs.login()

# 读取日交易数据获取涨停股票
print("读取日交易数据...")
daily = pd.read_csv("E:/code/model/process_data/process_data.csv")
daily["pct_chg"] = daily["pct_chg"].round(4)

# 筛选涨停股票
zt_data = daily[daily["pct_chg"] >= 9.9]
print(f"涨停记录: {len(zt_data)}")


# 转换为baostock代码格式
def ts_to_bs(ts_code):
    if ts_code.endswith(".SH"):
        return "sh." + ts_code.replace(".SH", "")
    return "sz." + ts_code.replace(".SZ", "")


# 获取样本数据(使用最近有涨停的日期)
sample = zt_data[zt_data["trade_date"].astype(str) >= "20250506"].head(500)
stock_dates = sample[["ts_code", "trade_date"]].drop_duplicates().values.tolist()

all_zting = []
processed = set()

for ts_code, trade_date in stock_dates:
    if ts_code in processed:
        continue

    bs_code = ts_to_bs(ts_code)
    date_str = str(trade_date)

    try:
        # 获取分时数据(使用日K)
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,time,open,high,low,close,volume",
            start_date=date_str,
            end_date=date_str,
            frequency="5",
            adjustflag="2",
        )

        data_list = []
        while rs.error_code == "0" and rs.next():
            data_list.append(rs.get_row_data())

        if data_list:
            df = pd.DataFrame(data_list, columns=rs.fields)

            if len(df) > 0:
                opens = df["open"].astype(float)
                highs = df["high"].astype(float)
                closes = df["close"].astype(float)

                # 检查是否涨停(最终涨幅>=9.9%)
                first_open = opens.iloc[0]
                last_close = closes.iloc[-1]

                if first_open > 0:
                    pct = (last_close - first_open) / first_open * 100

                    if pct >= 9.9:
                        # 找到首次涨停时间
                        for idx, row in df.iterrows():
                            open_p = float(row["open"])
                            high_p = float(row["high"])
                            close_p = float(row["close"])

                            # 封板: 价格不再变化(接近最高)
                            if high_p == close_p and high_p >= first_open * 1.099:
                                time_str = str(row["time"])
                                hour = int(time_str[8:10])
                                minute = int(time_str[10:12])

                                # 判断封板时段
                                if (
                                    hour == 9
                                    and minute >= 35
                                    or (hour == 10 and minute < 30)
                                ):
                                    period = "早盘"
                                elif (
                                    hour == 10
                                    and minute >= 30
                                    or (hour == 11 and minute < 30)
                                ):
                                    period = "午前"
                                elif hour == 13 or (hour == 14 and minute < 30):
                                    period = "午后"
                                elif hour == 14 and minute >= 30:
                                    period = "尾盘"
                                else:
                                    period = "其他"

                                all_zting.append(
                                    {
                                        "ts_code": ts_code,
                                        "trade_date": date_str,
                                        "period": period,
                                        "time": time_str,
                                        "pct": round(pct, 2),
                                    }
                                )
                                break  # 找到首次封板就记录
    except Exception as e:
        pass

    processed.add(ts_code)

    if len(processed) % 50 == 0:
        print(f"进度: {len(processed)}")

bs.logout()

if all_zting:
    result_df = pd.DataFrame(all_zting)
    result_df.to_csv("E:/code/model/raw_data/zt_period.csv", index=False)
    print(f"\n封板数据已保存: {len(result_df)}条")
    print(result_df["period"].value_counts())
else:
    print("未获取到封板数据")
