import os
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
    
    print(f"開始抓取 {stock_no} 過去一年的 K 線與成交量資料...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for date_str in reversed(date_str_list):
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date_str}&stockNo={stock_no}"
        
        try:
            response = requests.get(url, headers=headers, verify=False)
            json_data = response.json()
            
            if json_data.get("stat") == "OK":
                all_data.extend(json_data["data"])
                print(f"成功獲取 {date_str[:6]} 月份資料")
            else:
                print(f"{date_str[:6]} 月份無資料或查詢太過頻繁")
                
            time.sleep(3)
            
        except Exception as e:
            print(f"抓取 {date_str} 發生錯誤: {e}")
            
    columns = ['日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數', '最後未命名欄位']
    df = pd.DataFrame(all_data, columns=columns)
    
    df = df.drop(columns=['最後未命名欄位'])
    
    for col in ['成交股數', '開盤價', '最高價', '最低價', '收盤價']:
        df[col] = df[col].str.replace(',', '')
        
    return df

if __name__ == "__main__":
    try:
        etf_df = get_etf_kline_data("0050")
        etf_df.to_excel("0050_kline.xlsx", index=False)
        json_result = etf_df.to_json(orient="records", force_ascii=False)
        with open("etf_kline.json", "w", encoding="utf-8") as f:
            f.write(json_result)
            
        print("製表完成！")
        
    except Exception as main_error:
        print(f"執行時發生非預期錯誤: {main_error}")
