import twstock
import time
import datetime

# --- [設定區] 請在這裡填入您的 LINE Token ---
LINE_TOKEN = ""  # 稍後教您申請，暫時留空沒關係，會印在螢幕上

# --- [您的庫存清單] ---
# 格式: '股票代號': {'cost': 買入成本, 'highest': 買入後最高價}
MY_INVENTORY = {
    '2330': {'cost': 1300, 'highest': 1400},  # 假設您買了台積電
    '2603': {'cost': 190,  'highest': 190}    # 假設您買了長榮(目前套牢中?)
}

# --- [觀察名單] 想掃描哪些股票 ---
WATCH_LIST = ['2330', '2317', '2454', '2603', '2609', '2303'] 

def send_line_notify(msg):
    """發送 LINE 通知的函式"""
    print(f"【LINE通知】{msg}") # 先印在螢幕上
    if LINE_TOKEN:
        import requests
        url = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': 'Bearer ' + LINE_TOKEN}
        data = {'message': msg}
        requests.post(url, headers=headers, data=data)

def check_market_status():
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 開始掃描市場...")
    
    # 1. 掃描觀察名單 (找買點)
    for code in WATCH_LIST:
        try:
            stock = twstock.Stock(code)
            # 抓過去 200 天的歷史數據
            history_prices = stock.price[-200:] 
            
            if len(history_prices) < 50: continue # 資料太少跳過
            
            current_price = history_prices[-1] # 暫用收盤價，實盤可用 stock.realtime
            
            # 計算指標
            low_200 = min(history_prices) # 歷史低點
            ma5 = sum(history_prices[-5:]) / 5 # 5日均線
            
            # --- 策略 A: 歷史低點反彈 (您的策略 1) ---
            # 條件: 1. 股價在歷史低點 10% 範圍內 (接近谷底)
            #       2. 股價 > 5日均線 (開始往上跑)
            if current_price <= low_200 * 1.1 and current_price > ma5:
                msg = (f"\n🎯 發現【抄底機會】: {code}\n"
                       f"現價: {current_price}\n"
                       f"200日低點: {low_200}\n"
                       f"狀態: 位於低檔區且站上MA5")
                send_line_notify(msg)
                
        except Exception as e:
            print(f"掃描 {code} 時發生錯誤: {e}")
            
    # 2. 監控庫存 (您的策略 2)
    for code, data in MY_INVENTORY.items():
        try:
            stock = twstock.Stock(code)
            current_price = stock.price[-1]
            history_prices = stock.price[-200:]
            high_200 = max(history_prices)
            
            # 更新買入後的最高價紀錄
            if current_price > data['highest']:
                MY_INVENTORY[code]['highest'] = current_price
                
            # --- 策略 B: 歷史新高提醒 ---
            if current_price >= high_200:
                 msg = (f"\n🚀 持股【創新高】: {code}\n"
                        f"現價: {current_price}\n"
                        f"買入價: {data['cost']}\n"
                        f"建議: 續抱或設定停利")
                 send_line_notify(msg)
            
            # --- 策略 C: 高點回落警告 (移動停利) ---
            # 如果從波段最高點下跌超過 5%
            drawdown = (data['highest'] - current_price) / data['highest']
            if drawdown > 0.05:
                msg = (f"\n⚠️ 持股【回檔警告】: {code}\n"
                       f"現價: {current_price}\n"
                       f"波段最高: {data['highest']}\n"
                       f"回檔幅度: {drawdown*100:.1f}%\n"
                       f"建議: 檢查是否獲利了結")
                send_line_notify(msg)

        except Exception as e:
            print(f"監控持股 {code} 時發生錯誤: {e}")

if __name__ == "__main__":
    print("StockSniper 啟動中...")
    # 執行一次掃描
    check_market_status()
    print("\n掃描結束。若要持續運行，可結合 schedule 套件。")