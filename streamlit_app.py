import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="FF14 發家致富計算機", layout="wide")

# 初始化：如果 session 裡沒有歷史紀錄，就創一個空的 DataFrame
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        "商品名稱", "預期售價", "單件純利", "總利潤", "時薪", "時間"
    ])

st.title("FF14 發家致富計算機")

# --- 第一部分：計算區 ---
with st.container(border=True):
    st.subheader("📝 當前計算")
    col_input, col_res = st.columns([1, 1])

    with col_input:
        item_name = st.text_input("商品名稱", value="鐵礦")
        sell_price = st.number_input("預期單價 (NQ/HQ)", min_value=0, value=3000)
        batch_size = st.number_input("製作總量", min_value=1, value=99)
        mat_cost = st.number_input("材料總成本 (單件)", min_value=0, value=1500)
        crys_cost = st.number_input("水晶總成本 (單件)", min_value=0, value=200)
        time_per_item = st.number_input("製作單個秒數", min_value=1, value=3)

    # 計算邏輯
    revenue_net = sell_price * 0.95
    profit_per_item = revenue_net - (mat_cost + crys_cost)
    total_profit = profit_per_item * batch_size
    gil_per_hour = (total_profit / (time_per_item * batch_size)) * 3600 if total_profit != 0 else 0

    with col_res:
        st.metric("預估時薪", f"{gil_per_hour:,.0f} G/h")
        st.metric("單件純利", f"{profit_per_item:,.0f} G")
        
        # 存檔按鈕
        if st.button("🌟 加入收藏清單", use_container_width=True):
            new_data = {
                "商品名稱": item_name,
                "預期售價": sell_price,
                "單件純利": round(profit_per_item),
                "總利潤": round(total_profit),
                "時薪": round(gil_per_hour),
                "時間": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            # 將新紀錄疊加到歷史中
            st.session_state.history = pd.concat([pd.DataFrame([new_data]), st.session_state.history], ignore_index=True)
            st.toast(f"已加入：{item_name}")

# --- 第二部分：關注商品清單 (歷史計算) ---
st.divider()
st.subheader("📋 我的關注商品紀錄")

if not st.session_state.history.empty:
    # 使用 data_editor 讓你可以直接在網頁上修改或刪除
    edited_df = st.data_editor(
        st.session_state.history,
        use_container_width=True,
        num_rows="dynamic", # 允許動態刪除行
        column_config={
            "時薪": st.column_config.NumberColumn(format="%d G/h"),
            "總利潤": st.column_config.NumberColumn(format="%d G"),
        }
    )
    # 更新修改後的數據
    st.session_state.history = edited_df
    
    # 導出 CSV (方便你存到電腦裡)
    st.download_button(
        "📥 下載紀錄清單 (CSV)",
        data=st.session_state.history.to_csv(index=False).encode('utf-8-sig'),
        file_name="ff14_craft_history.csv",
        mime="text/csv"
    )
else:
    st.info("目前還沒有收藏的商品，快計算一個試試吧！")