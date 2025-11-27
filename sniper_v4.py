import twstock
import time
import datetime

# --- [設定區] ---
TEST_LIMIT = 5   # 測試抓 5 檔
START_CODE = '1101' # 從台泥開始抓 (跳過 00xx 的 ETF)

def get_stock_name(code):
    if code in twstock.codes:
        return twstock.codes[code].name
    return code

def check_market_status():
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 啟動 StockSniper V4 (修正資料抓取)...")
    
    # 1. 準備名單：過濾掉 4 碼以外的，且只抓 START_CODE 之後的
    all_codes = twstock.twse.keys()
    stock_codes = sorted([c for c in all_codes if len(c) == 4 and c >= START_CODE])
    
    # 取前幾檔測試
    target_codes = stock_codes[:TEST_LIMIT]
    print(f"掃描目標: {target_codes}")
    print("-" * 75)
    print(f"{'代號':<6} {'名稱':<8} {'現價':<8} {'狀態':<15} {'距低點%'}")
    print("-" * 75)

    for code in target_codes:
        try:
            stock = twstock.Stock(code)
            
            # --- 關鍵修正：強制抓取過去 1 年的資料 ---
            # 這樣才能湊滿 200 天。
            # fetch_from(year, month) 會抓該月到現在的所有資料
            # 這裡簡單設定從 2024 年 1 月開始抓 (確保資料夠多)
            stock.fetch_from(2024, 1)
            
            # 檢查資料長度
            if len(stock.price) < 200:
                print(f"{code:<6} (資料仍不足: {len(stock.price)}筆) - 跳過")
                continue
            
            name = get_stock_name(code)
            
            # 只取最後 200 筆來分析
            history_prices = stock.price[-200:]
            current_price = history_prices[-1]
            low_200 = min(history_prices)
            high_200 = max(history_prices)
            ma5 = sum(history_prices[-5:]) / 5
            
            # 計算距離
            diff_percent = ((current_price - low_200) / low_200) * 100
            
            # 判斷狀態
            status = "一般"
            if current_price <= low_200 * 1.1:
                status = "🟢接近低點"
                if current_price > ma5:
                    status = "🔥低檔起漲"
            elif current_price >= high_200:
                 status = "🔴創200日高"

            print(f"{code:<6} {name:<8} {current_price:<8.1f} {status:<15} {diff_percent:>.1f}%")
                
        except Exception as e:
            print(f"{code:<6} 讀取錯誤: {e}")
            
        # 抓長資料比較耗時，稍微休息久一點點
        time.sleep(1.5) 

    print("-" * 75)
    print("掃描完成。")

if __name__ == "__main__":
    check_market_status()