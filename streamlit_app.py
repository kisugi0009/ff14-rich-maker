import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="FF14 發家致富計算機", layout="wide")

# --- 1. 初始化與檔案上傳 ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        "商品名稱", "預期售價", "單件純利", "總利潤", "時薪", "時間"
    ])

# 用於連動採集成本的暫存狀態
if 'temp_mat_cost' not in st.session_state:
    st.session_state.temp_mat_cost = 20.0

st.title("FF14 發家致富計算機")

# 在側邊欄加入上傳功能
with st.sidebar:
    st.header("📂紀錄管理")
    uploaded_file = st.file_uploader("上傳之前的 CSV 紀錄", type=["csv"])
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            if "商品名稱" in uploaded_df.columns:
                st.session_state.history = uploaded_df
                st.success("✅ 紀錄載入成功！")
            else:
                st.error("❌ CSV 格式不符")
        except Exception as e:
            st.error(f"讀取錯誤: {e}")

# --- 2. 勞動成本評估區 (新增：決定要不要自己採集) ---
st.header("勞動成本評估")
with st.container(border=True):
    col_gather, col_opp = st.columns(2)
    
    with col_gather:
        st.subheader("採集數據")
        g_item_name = st.text_input("材料名稱", value="鐵礦")
        g_time = st.number_input("採集耗時 (分鐘)", min_value=1, value=30)
        g_yield = st.number_input("預計獲得數量", min_value=1, value=160)
        
    with col_opp:
        st.subheader("機會成本基準 (系統金)")
        # 整合你提供的系統金參考資料
        base_type = st.selectbox("選擇參考活動", [
            "隨機任務：練級 (約 2.4萬G / 20分)", 
            "100級理符搬運 (約 1.2萬G / 2分)", 
            "潛水艇平均收益 (約 40萬G / 5分)",
            "自定義"
        ])
        
        if "練級" in base_type:
            b_income, b_min = 24000, 20
        elif "理符" in base_type:
            b_income, b_min = 12000, 2
        elif "潛水艇" in base_type:
            b_income, b_min = 400000, 5
        else:
            b_income = st.number_input("基準收益 (Gil)", value=30000)
            b_min = st.number_input("基準耗時 (分鐘)", value=20)

    # 計算單個材料的時間價值
    val_per_min = b_income / b_min
    total_labor_val = g_time * val_per_min
    cost_per_unit = total_labor_val / g_yield

    st.divider()
    res_g1, res_g2 = st.columns(2)
    res_g1.metric("單個材料【時間成本】", f"{cost_per_unit:,.1f} G")
    res_g2.metric("這段時間的【產值損失】", f"{total_labor_val:,.0f} G")

    st.info(f"結論：如果板子上的 **{g_item_name}** 單價低於 **{cost_per_unit:,.1f} G**，直接板子買比較划算。")
    
    if st.button(f"將 {cost_per_unit:,.1f} G 套用到下方計算區", use_container_width=True):
        st.session_state.temp_mat_cost = cost_per_unit
        st.toast("已更新材料成本！")

# --- 3. 當前加工計算區 ---
st.header("加工利潤計算")
with st.container(border=True):
    col_input, col_res = st.columns([1, 1])

    with col_input:
        item_name = st.text_input("成品名稱", value="鐵錠")
        sell_price = st.number_input("預期售價 (單價)", min_value=0, value=800)
        batch_size = st.number_input("製作總量", min_value=1, value=99)
        # 這裡會接收來自上方的連動數值
        mat_cost = st.number_input("材料成本 (單件)", min_value=0.0, value=float(st.session_state.temp_mat_cost))
        crys_cost = st.number_input("水晶成本 (單件)", min_value=0, value=30)
        time_per_item = st.number_input("製作單個秒數", min_value=1, value=3)

    revenue_net = sell_price * 0.95
    profit_per_item = revenue_net - (mat_cost + crys_cost)
    total_profit = profit_per_item * batch_size
    gil_per_hour = (total_profit / (time_per_item * batch_size)) * 3600 if total_profit != 0 else 0

    with col_res:
        st.metric("預估加工時薪", f"{gil_per_hour:,.0f} G/h")
        st.metric("單件純利", f"{profit_per_item:,.1f} G")
        
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

# --- 4. 關注清單與下載 ---
st.divider()
st.subheader("我的關注商品紀錄")

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
    st.info("目前還沒有紀錄。")
    
# --- 側邊欄底部：製作者備註 ---
st.sidebar.divider() 

# 使用單一 div 設定字體大小，讓所有文字統一
st.sidebar.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        祝尼早日發家致富、盆滿缽滿(๑•̀ㅂ•́)و✧<br><br>
        Developed by @鳳凰 時偃
        <hr style='margin: 10px 0;'>
        <p style='color: #ffcc00;'>⚠️ 本工具尚不成熟，僅作輔助使用，切勿依賴。</p>
    </div>
    """, unsafe_allow_html=True)
