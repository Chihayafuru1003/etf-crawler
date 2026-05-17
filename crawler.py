import os
import time
import requests
import pandas as pd
from selenium import webdriver
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


if os.environ.get('GITHUB_ACTIONS') == 'true':
    print("偵測到 GitHub 雲端環境，啟用免瀏覽器 API 模式！")
    driver = None  # 在雲端不啟動瀏覽器，避免環境報錯
else:
    chrome_path_win = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_path_win_x86 = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    if os.path.exists(chrome_path_win) or os.path.exists(chrome_path_win_x86):
        from selenium.webdriver.chrome.service import Service
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        service = Service()
        driver = webdriver.Chrome(service=service, options=option)
        print("偵測到 Chrome，已成功啟動 Chrome 爬蟲核心")
    else:
        from selenium.webdriver.edge.service import Service
        option = webdriver.EdgeOptions()
        option.add_argument('--headless')
        service = Service()
        driver = webdriver.Edge(service=service, options=option)
        print("未偵測到 Chrome，已成功啟用 Edge 爬蟲核心")

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

try:
    etf_df = get_etf_kline_data("0050")
    
    etf_df.to_excel("0050_一年歷史K線資料.xlsx", index=False)
    
    json_result = etf_df.to_json(orient="records", force_ascii=False)
    with open("etf_kline.json", "w", encoding="utf-8") as f:
        f.write(json_result)
        
    print("製表完成！")

finally:
    if driver is not None:
        driver.quit()
