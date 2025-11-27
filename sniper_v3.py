import twstock
import time
import datetime
import random

# --- [設定區] ---
TEST_LIMIT = 5  # 先抓 5 檔就好，確認能跑出東西
WATCH_LIST = ['2330', '2603', '2317'] # 備用名單

def get_stock_name(code):
    if code in twstock.codes:
        return twstock.codes[code].name
    return code

def check_market_status():
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 啟動 StockSniper V3...")
    
    # --- 關鍵修正：只篩選 4 位數的股票代碼 ---
    # twstock.twse 包含上市股票與權證，我們過濾掉長度不等於 4 的
    all_codes = twstock.twse.keys()
    stock_codes = [c for c in all_codes if len(c) == 4]
    
    # 排序一下，確保從 1101 開始跑
    stock_codes.sort()
    
    print(f"資料庫總筆數: {len(all_codes)}")
    print(f"篩選後股票數: {len(stock_codes)} (僅含4碼上市股票)")
    
    # 測試模式：只取前 N 檔
    target_codes = stock_codes[:TEST_LIMIT]
    print(f"⚠️ 測試執行: 掃描前 {len(target_codes)} 檔: {target_codes}")

    print("-" * 75)
    print(f"{'代號':<6} {'名稱':<8} {'現價':<8} {'狀態':<15} {'距低點%'}")
    print("-" * 75)

    for code in target_codes:
        try:
            name = get_stock_name(code)
            
            # 1. 抓取資料 (即時+歷史)
            stock = twstock.Stock(code)
            
            # 判斷資料長度
            if len(stock.price) < 200:
                print(f"{code:<6} {name:<8} {'(資料不足)':<8} {'-':<15} {'-'}")
                continue
            
            # 抓取最近 200 天
            history_prices = stock.price[-200:]
            current_price = history_prices[-1]
            low_200 = min(history_prices)
            ma5 = sum(history_prices[-5:]) / 5
            
            # 計算距離
            diff_percent = ((current_price - low_200) / low_200) * 100
            
            # 判斷狀態
            status = "一般"
            if current_price <= low_200 * 1.1:
                status = "🟢低檔盤整"
                if current_price > ma5:
                    status = "🔥低檔起漲"
            elif current_price >= max(history_prices):
                 status = "🔴創新高"

            print(f"{code:<6} {name:<8} {current_price:<8.1f} {status:<15} {diff_percent:>.1f}%")
                
        except Exception as e:
            print(f"{code:<6} 錯誤: {e}")
            
        time.sleep(1) # 休息一秒

    print("-" * 75)
    print("掃描完成。")

if __name__ == "__main__":
    check_market_status()