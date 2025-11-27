import pandas as pd
import twstock
import time
import datetime

# --- 設定區 ---
SCAN_INTERVAL = 3  # 批次間隔秒數
CSV_FILE = 'stock_db.csv'

def load_database():
    try:
        # 讀取 CSV，並確保 code 欄位是字串
        df = pd.read_csv(CSV_FILE, dtype={'code': str})
        print(f"📚 已載入資料庫，共 {len(df)} 檔監控目標")
        return df
    except FileNotFoundError:
        print("❌ 找不到 stock_db.csv！請先執行 data_builder.py")
        return None

# [新增] 安全轉換函式：如果是 '-' 或壞掉的資料，回傳 None
def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def start_sniping():
    df = load_database()
    if df is None: return

    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] ⚡ StockSniper 極速掃描模式啟動...")
    print("=" * 70)
    print(f"{'代號':<6} {'名稱':<8} {'現價':<8} {'距離低點':<12} {'狀態判斷'}")
    print("=" * 70)

    target_codes = df['code'].tolist()
    BATCH_SIZE = 10
    
    for i in range(0, len(target_codes), BATCH_SIZE):
        batch = target_codes[i : i + BATCH_SIZE]
        
        try:
            realtime_data = twstock.realtime.get(batch)
            
            if realtime_data is None: # 網路問題或被擋
                print(f"⚠️ 批次 {batch[0]}... 抓取失敗 (回傳 None)")
                time.sleep(SCAN_INTERVAL)
                continue

            for code in batch:
                # 確保有抓到資料且資料格式正確
                if code not in realtime_data: continue
                if not realtime_data[code]['success']: continue
                
                # [關鍵修正] 使用 safe_float 來處理價格
                price_str = realtime_data[code]['realtime']['latest_trade_price']
                current_price = safe_float(price_str)
                
                # 如果價格是 None (代表沒成交或 '-' )，就跳過
                if current_price is None:
                    continue

                # 從 CSV 找紀錄
                record = df[df['code'] == code].iloc[0]
                low_200 = float(record['low_200'])
                high_200 = float(record['high_200'])
                ma5_ref = float(record['ma5_ref'])
                
                # 計算距離
                diff_percent = ((current_price - low_200) / low_200) * 100
                
                # 策略判斷
                status_msg = "Checking..."
                if current_price <= low_200 * 1.1:
                    status_msg = f"🟢 低檔盤整 ({diff_percent:.1f}%)"
                    if current_price > ma5_ref:
                        status_msg = f"🔥 底部翻揚! ({diff_percent:.1f}%)"
                elif current_price >= high_200:
                    status_msg = f"🚀 突破新高!"
                
                # 為了讓畫面乾淨，我們改成：
                # 「只有發現特殊狀態 (低檔/新高) 才印出來」
                # 或是「前 30 檔測試全部印出來」
                # 這裡保留全部印出方便您 Debug
                print(f"{code:<6} {record['name']:<8} {current_price:<8.1f} {diff_percent:>5.1f}%      {status_msg}")

        except Exception as e:
            # 印出錯誤但不中斷程式
            print(f"處理批次時發生未預期錯誤: {e}")
        
        time.sleep(1) # 休息一下

    print("=" * 70)
    print("掃描結束")

if __name__ == "__main__":
    start_sniping()