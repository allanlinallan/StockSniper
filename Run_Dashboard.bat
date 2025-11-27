@echo off
title StockSniper 戰情室
echo ==========================================
echo      正在啟動 StockSniper 戰情室...
echo ==========================================

:: 1. 切換到專案目錄 (使用 /d 確保跨磁碟切換成功)
cd /d D:\AI\StockSniper

:: 2. 啟動 Conda 環境
:: 注意：如果您的電腦沒把 conda 加入環境變數，可能需要用 call activate
call conda activate stock_ai

:: 3. 執行 Streamlit
echo.
echo 正在開啟瀏覽器...
streamlit run dashboard.py

:: 保持視窗開啟，以免有錯誤看不到
pause