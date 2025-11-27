import twstock
import pandas as pd
import time
import os
import random

# --- 設定區 ---
# 是否跑全市場？(True: 跑 1000 檔, False: 測試跑 30 檔)
# 建議第一次先設 False 跑跑看，確認流程順利
RUN_ALL = True  
TEST_COUNT = 30 
START_CODE = '1101' # 從台泥開始

def get_name(code):
    return twstock.codes[code].name if code in twstock.codes else code

def build_database():
    print("🚀 開始建立/更新 股票歷史數據庫...")
    
    # 1. 篩選股票名單 (只抓 4 碼上市股)
    all_codes = sorted([c for c in twstock.twse.keys() if len(c) == 4 and c >= START_CODE])
    
    if not RUN_ALL:
        print(f"⚠️ 測試模式：僅處理前 {TEST_COUNT} 檔股票")
        all_codes = all_codes[:TEST_COUNT]
    
    print(f"預計處理: {len(all_codes)} 檔股票 (抓歷史資料較慢，請耐心等待...)")
    
    data_list = []
    
    # 2. 開始迴圈抓資料
    for i, code in enumerate(all_codes):
        try:
            # 顯示進度條的概念
            print(f"[{i+1}/{len(all_codes)}] 處理 {code}...", end="\r")
            
            # 取得 13 個月前的日期 (多抓一個月當緩衝)
            past = datetime.datetime.now() - datetime.timedelta(days=395)
            
            stock = twstock.Stock(code)
            # 自動抓取那時候到現在的資料
            stock.fetch_from(past.year, past.month)
            
            # [資料清洗] 過濾掉 None 的價格
            clean_prices = [p for p in stock.price if p is not None]
            
            if len(clean_prices) < 200:
                continue # 資料不足跳過
                
            # 只看最近 200 天
            recent_200 = clean_prices[-200:]
            
            # 計算關鍵數據
            low_200 = min(recent_200)
            high_200 = max(recent_200)
            ma5 = sum(recent_200[-5:]) / 5
            ma20 = sum(recent_200[-20:]) / 20 # 多算一個月線備用
            
            # 存入列表
            data_list.append({
                'code': code,
                'name': get_name(code),
                'low_200': low_200,
                'high_200': high_200,
                'ma5_ref': ma5,   # 昨天的 MA5 (作為參考)
                'ma20_ref': ma20, # 昨天的 MA20
                'last_update': time.strftime("%Y-%m-%d")
            })
            
            # 隨機休息 (防擋)
            time.sleep(random.uniform(0.5, 1.0))
            
        except Exception as e:
            print(f"\n跳過 {code}: {e}")
            continue

    print("\n\n📊 資料抓取完成，正在存檔...")
    
    # 3. 存成 CSV 檔案 (這就是我們的小型資料庫)
    df = pd.DataFrame(data_list)
    df.to_csv('stock_db.csv', index=False, encoding='utf-8-sig')
    
    print(f"✅ 建檔完成！已儲存至 stock_db.csv (共 {len(df)} 筆)")
    print("接下來請執行 sniper_fast.py 進行快速掃描。")

if __name__ == "__main__":
    build_database()