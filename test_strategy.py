import twstock
from twstock import BestFourPoint
import time

# 設定目標：台積電(2330), 長榮(2603), 鴻海(2317)
target_stocks = ['2330', '2603', '2317']

print("="*50)
print("   StockSniper 狙擊手 - 初始測試")
print("="*50)

for code in target_stocks:
    print(f"\n[正在掃描] 股票代號: {code}")
    
    try:
        # 1. 抓取股票資料 (它會自動去網路抓歷史數據)
        stock = twstock.Stock(code)
        
        # 2. 取得最近一天的收盤價
        latest_price = stock.price[-1]
        latest_date = stock.date[-1].strftime('%Y-%m-%d')
        print(f"  > 日期: {latest_date} | 收盤價: {latest_price}")

        # 3. 使用四大買賣點演算法分析
        bfp = BestFourPoint(stock)
        buy = bfp.best_four_point_to_buy()
        sell = bfp.best_four_point_to_sell()

        # 4. 顯示結果
        if buy:
            print(f"  ★ 發現買點訊號!! 原因: {buy}")
        elif sell:
            print(f"  ▼ 發現賣點訊號!! 原因: {sell}")
        else:
            print("  - 目前無明顯訊號 (觀望)")
            
    except Exception as e:
        print(f"  X 發生錯誤: {e}")

    # 稍微停頓一下，避免對伺服器請求太快
    time.sleep(1)

print("\n" + "="*50)
print("測試完成")