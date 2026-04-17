import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="FF14 發家致富計算機", layout="wide")

# --- 1. 初始化與檔案上傳 ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        "商品名稱", "預期售價", "單件純利", "總利潤", "時薪", "時間"
    ])

st.title("FF14 發家致富計算機")

# 在側邊欄加入上傳功能
with st.sidebar:
    st.header("紀錄管理")
    uploaded_file = st.file_uploader("上傳之前的 CSV 紀錄", type=["csv"])
    if uploaded_file is not None:
        try:
            # 讀取上傳的 CSV 並更新到 session_state
            uploaded_df = pd.read_csv(uploaded_file)
            # 簡單檢查欄位是否正確
            if "商品名稱" in uploaded_df.columns:
                st.session_state.history = uploaded_df
                st.success("✅ 紀錄載入成功！")
            else:
                st.error("❌ CSV 格式不符，請上傳由此 App 下載的檔案。")
        except Exception as e:
            st.error(f"讀取錯誤: {e}")

# --- 2. 當前計算區 ---
with st.container(border=True):
    st.subheader("當前計算")
    col_input, col_res = st.columns([1, 1])

    with col_input:
        item_name = st.text_input("商品名稱", value="鐵礦")
        sell_price = st.number_input("預期單價 (NQ/HQ)", min_value=0, value=300)
        batch_size = st.number_input("製作總量", min_value=1, value=99)
        mat_cost = st.number_input("材料總成本 (單件)", min_value=0, value=20)
        crys_cost = st.number_input("水晶總成本 (單件)", min_value=0, value=10)
        time_per_item = st.number_input("製作單個秒數", min_value=1, value=3)

    revenue_net = sell_price * 0.95
    profit_per_item = revenue_net - (mat_cost + crys_cost)
    total_profit = profit_per_item * batch_size
    gil_per_hour = (total_profit / (time_per_item * batch_size)) * 3600 if total_profit != 0 else 0

    with col_res:
        st.metric("預估時薪", f"{gil_per_hour:,.0f} G/h")
        st.metric("單件純利", f"{profit_per_item:,.0f} G")
        
        if st.button("加入關注清單", use_container_width=True):
            new_data = {
                "商品名稱": item_name,
                "預期售價": sell_price,
                "單件純利": round(profit_per_item),
                "總利潤": round(total_profit),
                "時薪": round(gil_per_hour),
                "時間": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.history = pd.concat([pd.DataFrame([new_data]), st.session_state.history], ignore_index=True)
            st.toast(f"已加入：{item_name}")

# --- 3. 關注清單與下載 ---
st.divider()
st.subheader("📋 我的關注商品紀錄")

if not st.session_state.history.empty:
    edited_df = st.data_editor(
        st.session_state.history,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "時薪": st.column_config.NumberColumn(format="%d G/h"),
            "總利潤": st.column_config.NumberColumn(format="%d G"),
        }
    )
    st.session_state.history = edited_df
    
    st.download_button(
        "下載目前紀錄 (CSV)",
        data=st.session_state.history.to_csv(index=False).encode('utf-8-sig'),
        file_name="ff14_craft_history.csv",
        mime="text/csv"
    )
else:
    st.info("目前還沒有紀錄。你可以從左側上傳之前的 CSV，或是開始新的計算！")
