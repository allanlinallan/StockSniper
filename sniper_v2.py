import twstock
import time
import datetime
import random

# --- [設定區] ---
# 是否要掃描全部上市股票？
SCAN_ALL_STOCKS = True

# 測試限制：為了避免跑太久，先只跑前 20 檔 (設為 None 則跑全部，約需 30-40 分鐘)
TEST_LIMIT = 20  

# 您的觀察名單 (如果 SCAN_ALL_STOCKS = False，就只跑這個)
WATCH_LIST = ['2330', '2603', '2317', '2454', '2609']

def get_stock_name(code):
    """取得股票名稱"""
    try:
        if code in twstock.codes:
            return twstock.codes[code].name
        return "未知"
    except:
        return "未知"

def check_market_status():
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 啟動 StockSniper 狙擊掃描...")
    
    # 決定要掃描的名單
    if SCAN_ALL_STOCKS:
        # 取得所有上市股票代號 (TPEx 是上櫃，這裡先只抓上市)
        target_codes = list(twstock.twse.keys())
        print(f"模式: 全市場掃描 (上市股票共 {len(target_codes)} 檔)")
    else:
        target_codes = WATCH_LIST
        print(f"模式: 觀察名單掃描 (共 {len(target_codes)} 檔)")

    # 測試限制
    if TEST_LIMIT and len(target_codes) > TEST_LIMIT:
        print(f"⚠️ 測試模式: 僅掃描前 {TEST_LIMIT} 檔股票...")
        target_codes = target_codes[:TEST_LIMIT]

    print("-" * 60)
    print(f"{'代號':<6} {'名稱':<8} {'現價':<8} {'低點狀態(距200日低)'}")
    print("-" * 60)

    # 開始迴圈
    for code in target_codes:
        try:
            name = get_stock_name(code)
            
            # 1. 抓取資料
            stock = twstock.Stock(code)
            
            # 優化：只抓最近 200 天就好，不用抓全部歷史，節省時間
            # 注意：twstock 的 fetch_from 比較慢，這裡為了演示邏輯先用預設抓取
            if len(stock.price) < 200:
                # 資料不足，跳過
                continue
            
            history_prices = stock.price[-200:]
            current_price = history_prices[-1]
            
            # 計算指標
            low_200 = min(history_prices)
            ma5 = sum(history_prices[-5:]) / 5
            
            # 計算距離歷史低點的百分比
            diff_percent = ((current_price - low_200) / low_200) * 100
            
            # 顯示進度 (因為要跑很久，印出來讓您知道它活著)
            # 格式說明: <6 代表靠左對齊佔6格
            print(f"{code:<6} {name:<8} {current_price:<8.1f} {diff_percent:>.1f}%")

            # --- 策略核心 ---
            # 條件: 距離低點 10% 以內 且 股價 > 5日均線
            if current_price <= low_200 * 1.1 and current_price > ma5:
                print(f"  >>> 🔥 發現狙擊目標: {name} ({code}) !!")
                print(f"      現價 {current_price} 接近歷史低點 {low_200} 且站上 MA5")
                # 這裡未來可以放 LINE 通知
                
        except Exception as e:
            print(f"X 跳過 {code}: 資料讀取錯誤")
            continue
            
        # 為了禮貌，每次抓完稍微休息一下 (避免被證交所封鎖 IP)
        # 如果要掃全台股，這個 sleep 時間要權衡
        time.sleep(random.uniform(0.5, 1.0)) 

    print("-" * 60)
    print("掃描完成。")

if __name__ == "__main__":
    check_market_status()