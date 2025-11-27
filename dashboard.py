import streamlit as st
import pandas as pd
import glob
import os

st.set_page_config(page_title="StockSniper 戰情室", layout="wide")
st.title("🎯 StockSniper 股市狙擊手 - 戰情室")
st.markdown("---")

# 1. 自動讀取最新報表
list_of_files = glob.glob('sniper_report*.csv') 
if not list_of_files:
    st.error("❌ 找不到報表檔案！請先執行 sniper_news.py 進行掃描。")
    st.stop()

latest_file = max(list_of_files, key=os.path.getctime)
st.sidebar.info(f"📅 報表來源：{os.path.basename(latest_file)}")

try:
    # 強制將代號讀取為字串，避免後續相加出錯
    df = pd.read_csv(latest_file, dtype={'代號': str})
    
    # 相容性檢查：如果舊報表沒有這個欄位，給予預設值
    if '距低點(%)' not in df.columns: df['距低點(%)'] = 0.0
        
except Exception as e:
    st.error(f"檔案讀取失敗: {e}")
    st.stop()

# --- 2. 側邊欄篩選器 ---
st.sidebar.header("🔍 戰略篩選")

# 定義新版的所有訊號
ALL_POSSIBLE_SIGNALS = [
    "🚀 突破新高", "🔥 即將創高", 
    "🐂 強勢多頭", "📉 高檔回檔",
    "⚡ 底部翻揚", "💤 低檔盤整", "🟢 歷史極低",
    "⚖️ 區間震盪"
]

# 找出目前 CSV 裡實際存在的訊號
existing_signals = df['訊號'].unique().tolist() if not df.empty else []

# [關鍵修正] 計算交集：只將「同時存在於 CSV」且「符合清單」的訊號設為預設勾選
# 這能完美防止 "default value is not part of options" 錯誤
valid_defaults = [s for s in existing_signals if s in ALL_POSSIBLE_SIGNALS]

selected_signals = st.sidebar.multiselect(
    "📡 訊號類型 (多選)",
    options=ALL_POSSIBLE_SIGNALS, # 下拉選單顯示所有可能性
    default=valid_defaults        # 預設只勾選目前有的
)

price_range = st.sidebar.slider("💰 價格範圍 (元)", 0, 2000, (10, 200))
diff_range = st.sidebar.slider("📉 距低點範圍 (%)", 0.0, 100.0, (0.0, 50.0))
news_keyword = st.sidebar.text_input("📰 新聞關鍵字 (例: 營收, 獲利)")

# --- 3. 篩選邏輯 ---
if not df.empty:
    mask = (
        (df['現價'] >= price_range[0]) & 
        (df['現價'] <= price_range[1]) &
        (df['訊號'].isin(selected_signals)) &
        (df['距低點(%)'] >= diff_range[0]) & 
        (df['距低點(%)'] <= diff_range[1])
    )
    
    if news_keyword:
        mask = mask & (df['AI備註'].str.contains(news_keyword, na=False) | df['新聞快訊'].str.contains(news_keyword, na=False))

    filtered_df = df[mask]
else:
    filtered_df = pd.DataFrame()

# --- 4. 顯示結果 ---
st.subheader(f"📊 篩選結果：共 {len(filtered_df)} 檔")

if not filtered_df.empty:
    # 定義顏色格式
    def color_signal(val):
        color = 'black'
        if '新高' in val: color = 'red'
        elif '底部' in val or '翻揚' in val: color = 'green'
        elif '即將' in val: color = 'orange'
        elif '極低' in val: color = 'blue'
        return f'color: {color}; font-weight: bold;'

    st.dataframe(
        filtered_df.style.applymap(color_signal, subset=['訊號']),
        column_config={
            "代號": st.column_config.TextColumn("代號"),
            "現價": st.column_config.NumberColumn("現價", format="$%.1f"),
            "距低點(%)": st.column_config.NumberColumn("距低點", format="%.1f%%"),
            "AI備註": st.column_config.TextColumn("AI 分析", width="medium"),
            "新聞快訊": st.column_config.TextColumn("最新新聞", width="large"),
        },
        use_container_width=True, # 使用新版參數
        hide_index=True
    )
    
    st.markdown("### 📝 個股詳細資訊")
    
    # 這裡確保代號是字串，不會報錯
    stock_options = filtered_df['代號'].astype(str) + " " + filtered_df['名稱']
    target = st.selectbox("請選擇一檔股票:", stock_options)
    
    if target:
        code = target.split(" ")[0]
        row = filtered_df[filtered_df['代號'] == code].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("價格", f"{row['現價']} 元", row['訊號'])
        c2.metric("位階", f"距低點 {row['距低點(%)']}%")
        
        st.markdown(f"[📈 前往 Yahoo 股市: {code}](https://tw.stock.yahoo.com/quote/{code})")
        
        if pd.notna(row.get('新聞快訊')) and row['新聞快訊'] != "無近期新聞":
             st.info(f"📰 最新標題: {row['新聞快訊']}")
             
        if pd.notna(row.get('AI備註')) and row['AI備註'] != "-":
            st.success(f"🤖 AI 分析: {row['AI備註']}")

else:
    st.warning("⚠️ 沒有符合條件的股票，請放寬篩選條件。")

if st.sidebar.button("🔄 刷新報表"):
    st.rerun()