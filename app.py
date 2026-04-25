import streamlit as st
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & ASSET ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    asset_type = st.selectbox("Select Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"])
    symbol = st.text_input("Enter Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    if "balance" not in st.session_state:
        st.session_state.balance = 2146.11
    
    st.metric("Current Balance", f"${round(st.session_state.balance, 2)}")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)

    st.header("🌍 News Filter")
    # THE MASTER LOCK: Default is OFF
    news_ok = st.toggle("No High Impact News", value=False)
    
    if not news_ok:
        st.error("🚨 SYSTEM LOCKED: News must be cleared.")

# ---------------- DYNAMIC HEADLINE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Asset: {symbol} | Mode: {asset_type} | Server Time: {dt_string}")
st.markdown("---")

# ---------------- QUAD TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)

# --- 4H BIAS ---
c4h.subheader("⏳ 4H BIAS")
# Locked strictly by News Filter
htf_bias = c4h.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", disabled=not news_ok)
h_input_lock = not news_ok or htf_bias == "Select..."

s4_h = c4h.number_input("Swing High", value=0.0, format="%.2f", key="s4h", disabled=h_input_lock)
s4_l = c4h.number_input("Swing Low", value=0.0, format="%.2f", key="s4l", disabled=h_input_lock)
bias_4h_ok = c4h.checkbox("4H Confirmed", key="4h_c", disabled=h_input_lock or not (s4_h > 0 and s4_l > 0))

# --- 1H STRUC ---
c1h.subheader("⏱️ 1H STRUC")
# FIXED: Now strictly locked by news_ok AND 4H Confirmation
itf_trend = c1h.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", disabled=not news_ok or not bias_4h_ok)
i_input_lock = not news_ok or not bias_4h_ok or itf_trend == "Select..."

s1_h = c1h.number_input("Swing High", value=0.0, format="%.2f", key="s1h", disabled=i_input_lock)
s1_l = c1h.number_input("Swing Low", value=0.0, format="%.2f", key="s1l", disabled=i_input_lock)
bias_1h_ok = c1h.checkbox("1H Confirmed", key="1h_c", disabled=i_input_lock or not (s1_h > 0 and s1_l > 0))

# --- 30M SHIFT ---
c30m.subheader("⚡ 30M SHIFT")
# FIXED: Now strictly locked by news_ok AND 1H Confirmation
t30_trend = c30m.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t", disabled=not news_ok or not bias_1h_ok)
m30_input_lock = not news_ok or not bias_1h_ok or t30_trend == "Select..."

s30_h = c30m.number_input("Swing High", value=0.0, format="%.2f", key="s30h", disabled=m30_input_lock)
s30_l = c30m.number_input("Swing Low", value=0.0, format="%.2f", key="s30l", disabled=m30_input_lock)
bias_30m_ok = c30m.checkbox("30M Confirmed", key="30m_c", disabled=m30_input_lock or not (s30_h > 0 and s30_l > 0))

# --- 15M ENTRY ---
c15m.subheader("🎯 15M ENTRY")
# FIXED: Now strictly locked by news_ok AND 30M Confirmation
t15_trend = c15m.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t", disabled=not news_ok or not bias_30m_ok)
m15_input_lock = not news_ok or not bias_30m_ok or t15_trend == "Select..."

s15_h = c15m.number_input("Swing High", value=0.0, format="%.2f", key="s15h", disabled=m15_input_lock)
s15_l = c15m.number_input("Swing Low", value=0.0, format="%.2f", key="s15l", disabled=m15_input_lock)
bias_15m_ok = c15m.checkbox("15M Confirmed", key="15m_c", disabled=m15_input_lock or not (s15_h > 0 and s15_l > 0))

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
# All following steps only work if 15M is confirmed AND News is clear
ready_to_trade = news_ok and bias_15m_ok

col_poi, col_exec = st.columns([1, 2])
with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("POI Type", ["Select...", "Swing High/Low", "Supply/Demand", "Order Block", "FVG"], disabled=not ready_to_trade)
    zone_price = st.number_input("Entry Zone", value=0.0, format="%.2f", disabled=not ready_to_trade)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    entry = st.number_input("Entry Price", value=0.0, format="%.2f", disabled=not (zone_price > 0))
    # Calculations for Lots/Risk would follow here...
