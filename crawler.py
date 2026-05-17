import time
import requests
import pandas as pd
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_etf_kline_data(stock_no="0050"):
    current_date = pd.Timestamp.now()
    date_list = [current_date - pd.DateOffset(months=i) for i in range(12)]
    date_str_list = [d.strftime("%Y%m%d") for d in date_list]
    all_data = []

    print(f"開始抓取 {stock_no} 過去一年資料...")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    for date_str in reversed(date_str_list):
        # 這裡改用單一引號字串，完全避免括號拼接出錯的可能性
        url = f"https://twse.com.tw{date_str}&stockNo={stock_no}"

        try:
            response = requests.get(url, headers=headers, timeout=15, verify=False)
            try:
                json_data = response.json()
            except Exception:
                print(f"{date_str} JSON 解析失敗")
                continue

            if json_data.get("stat") == "OK" and "data" in json_data:
                all_data.extend(json_data["data"])
                print(f"成功抓取 {date_str[:6]} 月份資料")
            else:
                print(f"{date_str[:6]} 無資料或請求過快（回應狀態: {json_data.get('stat')}）")
            
            time.sleep(4)

        except Exception as e:
            print(f"{date_str} 發生錯誤: {e}")

    if not all_data:
        print("錯誤：完全沒有抓取到任何資料，請檢查網路或 API。")
        return pd.DataFrame()

    columns = ['日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']
    df = pd.DataFrame(all_data)
    
    if df.shape[1] >= len(columns):
        df = df.iloc[:, :len(columns)]
        df.columns = columns
    else:
        print("警告：回傳資料欄位數少於預期")
        return df

    for col in ['成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '成交筆數']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)

    return df

if __name__ == "__main__":
    try:
        etf_df = get_etf_kline_data("0050")

        if not etf_df.empty:
            excel_filename = "0050_kline.xlsx"
            json_filename = "etf_kline.json"

            etf_df.to_excel(excel_filename, index=False)

            json_result = etf_df.to_json(orient="records", force_ascii=False)
            with open(json_filename, "w", encoding="utf-8") as f:
                f.write(json_result)

            print("Python 端的資料更新完成！")
        else:
            print("因無資料，未產生新的實體檔案")

    except Exception as main_error:
        print(f"主程式錯誤: {main_error}")
