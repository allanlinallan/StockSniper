import pandas as pd
import twstock
import time
import datetime
import random
import requests

# --- 設定區 ---
CSV_FILE = 'stock_db.csv'
REPORT_FILE = f'sniper_report_{datetime.date.today()}.csv' # 存檔檔名加上日期
BATCH_SIZE = 8

def load_database():
    try:
        df = pd.read_csv(CSV_FILE, dtype={'code': str})
        print(f"📚 已載入資料庫，共 {len(df)} 檔監控目標")
        return df
    except FileNotFoundError:
        print("❌ 找不到 stock_db.csv！")
        return None

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def start_sniping():
    df = load_database()
    if df is None: return

    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 🛡️ StockSniper 穩定掃描模式啟動...")
    print("=" * 70)
    print(f"{'代號':<6} {'名稱':<8} {'現價':<8} {'距離低點':<12} {'狀態判斷'}")
    print("=" * 70)

    target_codes = df['code'].tolist()
    
    # 準備一個清單來存結果
    found_targets = []
    
    i = 0
    while i < len(target_codes):
        batch = target_codes[i : i + BATCH_SIZE]
        
        try:
            realtime_data = twstock.realtime.get(batch)
            
            if realtime_data is None:
                raise Exception("Empty Response")

            for code in batch:
                if code not in realtime_data or not realtime_data[code]['success']:
                    continue
                
                price_str = realtime_data[code]['realtime']['latest_trade_price']
                current_price = safe_float(price_str)
                
                if current_price is None: continue

                record = df[df['code'] == code].iloc[0]
                low_200 = float(record['low_200'])
                high_200 = float(record['high_200'])
                ma5_ref = float(record['ma5_ref'])
                
                diff_percent = ((current_price - low_200) / low_200) * 100
                
                status_msg = ""
                status_type = "" # 用來分類存檔
                
                # 策略: 距離低點 10% 內
                if current_price <= low_200 * 1.1:
                    status_type = "低檔盤整"
                    status_msg = f"🟢 低檔盤整 ({diff_percent:.1f}%)"
                    if current_price > ma5_ref:
                        status_type = "底部翻揚"
                        status_msg = f"🔥 底部翻揚! ({diff_percent:.1f}%)"
                # 策略: 創新高
                elif current_price >= high_200:
                    status_type = "突破新高"
                    status_msg = f"🚀 突破新高!"

                # 如果有訊號，印出來並存起來
                if status_type:
                     print(f"{code:<6} {record['name']:<8} {current_price:<8.1f} {diff_percent:>5.1f}%      {status_msg}")
                     
                     # 加入結果清單
                     found_targets.append({
                         '代號': code,
                         '名稱': record['name'],
                         '現價': current_price,
                         '距低點(%)': round(diff_percent, 2),
                         '訊號類型': status_type,
                         '詳細': status_msg,
                         '時間': datetime.datetime.now().strftime('%H:%M')
                     })

            i += BATCH_SIZE
            time.sleep(random.uniform(3, 6))

        except Exception as e:
            err_msg = str(e)
            # 簡化錯誤訊息顯示
            if "tlong" in err_msg: # 忽略 8081 那種小錯誤
                print(f"⚠️ 批次跳過 (資料格式錯誤)")
                i += BATCH_SIZE
                continue
                
            if "Connection aborted" in err_msg or "RemoteDisconnected" in err_msg:
                print(f"🛑 IP 被封鎖，冷卻 60 秒...")
                time.sleep(60)
                print("▶️ 恢復...")
            else:
                print(f"⚠️ 未知錯誤: {err_msg}，跳過此批...")
                i += BATCH_SIZE
                time.sleep(3)

    print("=" * 70)
    print("掃描結束")
    
    # --- 最後：將結果存成 CSV 報表 ---
    if found_targets:
        result_df = pd.DataFrame(found_targets)
        # 依照訊號類型排序 (把 '底部翻揚' 排前面)
        result_df = result_df.sort_values(by='訊號類型', ascending=False)
        
        result_df.to_csv(REPORT_FILE, index=False, encoding='utf-8-sig')
        print(f"\n✅ 恭喜！已發現 {len(found_targets)} 檔機會，報表已儲存為: {REPORT_FILE}")
    else:
        print("\n今天很平靜，沒有發現符合條件的股票。")

if __name__ == "__main__":
    start_sniping()