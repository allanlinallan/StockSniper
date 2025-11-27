
   StockSniper 股市狙擊手 - 系統安裝指南 (Windows)
   
   ⚠️ 免責聲明 (Disclaimer)： 本專案僅供程式交易研究與資訊整理之用，不構成任何投資建議。使用者應自行承擔投資風險，作者不負任何盈虧之責。


[重要觀念說明]
本專案使用 "Miniconda" 來管理 Python 環境。
Miniconda 安裝包已內含 Python 核心，因此您「不需要」另外去 Python 官網下載安裝，
以免電腦裡有多個 Python 版本互相衝突。

[第一階段] 下載與安裝基礎工具 (Miniconda)
-------------------------------------------------------------------
1. 下載 Miniconda (這就是您的 Python 安裝程式):
   請前往官方下載頁面：
   https://docs.conda.io/en/latest/miniconda.html#windows-installers
   
   * 請選擇列表中的: "Miniconda3 Windows 64-bit" 進行下載。

2. 安裝步驟:
   A. 點擊執行下載的安裝檔 (.exe)。
   B. 一路點擊 "Next" 或 "I Agree"。
   C. 安裝路徑建議維持預設。
   D. 【安裝選項】(Advanced Options)：
      - 建議勾選 "Register Miniconda3 as my default Python 3.10"。
      - (選用) "Add Miniconda3 to my PATH..." 建議「不要」勾選 (紅色字體)，
        我們之後使用專屬的 Anaconda Prompt 來操作會比較穩定。
   E. 點擊 "Install" 直到完成。

[第二階段] 建立專案環境 (這裡會安裝 Python 3.10)
-------------------------------------------------------------------
請全部在「Anaconda Prompt」視窗中進行。

1. 開啟終端機:
   點擊 Windows 「開始」按鈕 -> 搜尋 "Anaconda Prompt (Miniconda3)" 並開啟。
   (以後我們都用這個黑色視窗來下指令)

2. 切換到 D 槽並建立資料夾:
   d:
   mkdir AI\StockSniper
   cd AI\StockSniper

3. 建立虛擬環境:
   (這行指令會自動下載並安裝 Python 3.10 到此環境中)
   
   conda create -n stock_ai python=3.10 -y

4. 啟動環境:
   (看到最前面出現 (stock_ai) 代表成功進入環境)
   
   conda activate stock_ai

[第三階段] 安裝必要的程式庫
-------------------------------------------------------------------
1. 安裝 TA-Lib (金融技術指標庫):
   * 這是最難裝的套件，使用 conda 可以一鍵完成。
   
   conda install -c conda-forge ta-lib -y

2. 安裝其他 Python 套件:
   
   pip install twstock pandas requests schedule line-bot-sdk beautifulsoup4 lxml streamlit

[第四階段] 初始化資料庫
-------------------------------------------------------------------
1. 執行建檔程式 (需時約 30-40 分鐘):
   
   python data_builder.py

2. 當看到「✅ 建檔完成」且資料夾中出現 stock_db.csv，安裝即完成。

===================================================================

執行程式 請參考
使用說明檔 (README).txt



<img width="1898" height="905" alt="image" src="https://github.com/user-attachments/assets/bef2d231-05cc-47d2-8323-602406852341" />

<img width="1531" height="478" alt="image" src="https://github.com/user-attachments/assets/7f5bd6eb-ba9f-49d8-b922-e9d902bc8a16" />




⚠️ 免責聲明 (Disclaimer)： 本專案僅供程式交易研究與資訊整理之用，不構成任何投資建議。使用者應自行承擔投資風險，作者不負任何盈虧之責。
