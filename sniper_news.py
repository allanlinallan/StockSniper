import pandas as pd
import twstock
import time
import datetime
import random
import requests
from bs4 import BeautifulSoup

# --- 設定區 ---
CSV_FILE = 'stock_db.csv'
REPORT_FILE = f'sniper_report_news_{datetime.date.today()}.csv'
BATCH_SIZE = 5

def load_database():
    try:
        df = pd.read_csv(CSV_FILE, dtype={'code': str})
        return df
    except FileNotFoundError:
        print("❌ 找不到 stock_db.csv！")
        return None

def safe_float(value):
    try:
        return float(value)
    except:
        return None

def scan_news(stock_name):
    """(維持原樣) 搜尋 Google News"""
    try:
        query = f"{stock_name}"
        url = f"https://news.google.com/rss/search?q={query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        resp = requests.get(url, timeout=3) # 加快 timeout
        soup = BeautifulSoup(resp.content, features="xml")
        items = soup.find_all('item')
        
        if not items: return "無近期新聞", 0, "消息平淡"

        latest_title = items[0].title.text
        score = 0
        keywords_pos = ['營收', '創高', '大增', '買超', '旺季', '成長', '強勢', '填息', '獲利', '漲停', '法說']
        keywords_neg = ['虧損', '衰退', '賣超', '下修', '重挫', '跌停', '疲弱', '利空', '斬腰']
        
        found_k = []
        for item in items[:3]: # 只看前3則加快速度
            title = item.title.text
            for k in keywords_pos:
                if k in title: 
                    score += 1
                    if k not in found_k: found_k.append(k)
            for k in keywords_neg:
                if k in title: 
                    score -= 1
                    if k not in found_k: found_k.append(k)

        remark = "消息中性"
        if score >= 1: remark = f"🔴 偏多 ({','.join(found_k)})"
        if score < 0: remark = f"🟢 偏空 ({','.join(found_k)})"
            
        return latest_title, score, remark
    except:
        return "讀取失敗", 0, "N/A"

def get_market_status(price, low_200, high_200, ma5):
    """
    [核心升級] 更細膩的分類邏輯
    """
    # 1. 創高區
    if price >= high_200:
        return "🚀 突破新高"
    if price >= high_200 * 0.95:
        return "🔥 即將創高" # 距離高點 < 5%

    # 2. 低檔區
    if price <= low_200 * 1.05:
        return "🟢 歷史極低" # 距離低點 < 5% (地板價)
    if price <= low_200 * 1.15: # 放寬到 15%
        if price > ma5:
            return "⚡ 底部翻揚" # 轉強
        else:
            return "💤 低檔盤整" # 還在睡

    # 3. 中間趨勢區 (強勢整理 vs 弱勢反彈)
    # 判斷位置: (現價 - 低點) / (高點 - 低點)
    position = (price - low_200) / (high_200 - low_200)
    
    if position > 0.7: # 在高檔區 (前 30% 強勢區)
        if price > ma5:
            return "🐂 強勢多頭"
        else:
            return "📉 高檔回檔" # 強勢股休息
            
    if position < 0.3: # (上面已經被低檔區抓走了，這裡通常抓不到，但也許有漏網)
        return "💤 低檔盤整"

    return "⚖️ 區間震盪" # 不上不下

def start_sniping():
    df = load_database()
    if df is None: return

    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 📰 StockSniper 多策略版啟動...")
    print("=" * 100)
    print(f"{'代號':<6} {'名稱':<6} {'現價':<8} {'距低點':<8} {'狀態分類':<12} {'AI 備註'}")
    print("=" * 100)

    target_codes = df['code'].tolist()
    found_targets = []
    
    i = 0
    while i < len(target_codes):
        batch = target_codes[i : i + BATCH_SIZE]
        try:
            realtime_data = twstock.realtime.get(batch)
            if realtime_data is None: raise Exception("Empty")

            for code in batch:
                if code not in realtime_data or not realtime_data[code]['success']: continue
                price_str = realtime_data[code]['realtime']['latest_trade_price']
                current_price = safe_float(price_str)
                if current_price is None: continue

                record = df[df['code'] == code].iloc[0]
                low = float(record['low_200'])
                high = float(record['high_200'])
                ma5 = float(record['ma5_ref'])
                
                diff_percent = ((current_price - low) / low) * 100
                
                # [核心] 取得分類狀態
                status_type = get_market_status(current_price, low, high, ma5)
                
                # 只有 "區間震盪" 我們可能不想看，其他都存起來
                if status_type != "⚖️ 區間震盪":
                    # 簡單過濾一下新聞，不用每檔都抓，只抓比較極端的
                    ai_remark = ""
                    news_title = ""
                    # 只有 強勢 或 底部翻揚 才去浪費時間抓新聞
                    if "突破" in status_type or "底部" in status_type or "創高" in status_type:
                        news_title, _, ai_remark = scan_news(record['name'])
                    else:
                        ai_remark = "-" # 省略

                    print(f"{code:<6} {record['name']:<6} {current_price:<8.1f} {diff_percent:>6.1f}%   {status_type:<12} {ai_remark}")
                    
                    found_targets.append({
                        '代號': code,
                        '名稱': record['name'],
                        '現價': current_price,
                        '距低點(%)': round(diff_percent, 1),
                        '訊號': status_type, # 這裡現在會有很多種狀態了
                        '新聞快訊': news_title,
                        'AI備註': ai_remark,
                        '綜合建議': status_type # 暫時用狀態當建議
                    })

            i += BATCH_SIZE
            time.sleep(random.uniform(1.5, 3)) # 稍微快一點

        except Exception as e:
            if "Connection" in str(e):
                print(f"🛑 IP 冷卻中... (60s)")
                time.sleep(60)
            i += BATCH_SIZE

    print("=" * 100)
    if found_targets:
        result_df = pd.DataFrame(found_targets)
        result_df.to_csv(REPORT_FILE, index=False, encoding='utf-8-sig')
        print(f"✅ 報表已產生: {REPORT_FILE}")

if __name__ == "__main__":
    start_sniping()