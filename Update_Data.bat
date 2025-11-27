@echo off
title StockSniper 資料更新精靈
echo ==========================================
echo      正在執行全市場掃描 (含新聞分析)...
echo      掃描過程約需 5-10 分鐘，請耐心等待
echo ==========================================

cd /d D:\AI\StockSniper

:: 啟動環境
call conda activate stock_ai

:: 執行掃描程式
python sniper_news.py

echo.
echo ==========================================
echo      掃描完成！
echo      請執行 Run_Dashboard.bat 查看結果
echo ==========================================
pause