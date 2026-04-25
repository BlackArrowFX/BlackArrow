import streamlit as st
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & NEWS ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    asset_type = st.selectbox("Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"])
    symbol = st.text_input("Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    if "balance" not in st.session_state: st.session_state.balance = 2146.11
    
    st.metric("Current Balance", f"${round(st.session_state.balance, 2)}")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    current_risk_usd = st.session_state.balance * (st.slider("Risk %", 0.25, 5.0, 1.0)/100) if risk_method == "Percentage (%)" else st.number_input("Risk $", value=50.0)

    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News", value=False)
    if not news_ok: st.error("🚨 SYSTEM LOCKED: News Filter")

# ---------------- QUAD TIMEFRAME ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol}")
st.markdown("---")
c4h, c1h, c30m, c15m = st.columns(4)

# 4H
with c4h:
    st.subheader("⏳ 4H BIAS")
    htf_bias = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", disabled=not news_ok)
    h_lock = not news_ok or htf_bias == "Select..."
    s4_h = st.number_input("Swing High", value=0.0, format="%.2f", key="s4h", disabled=h_lock)
    s4_l = st.number_input("Swing Low", value=0.0, format="%.2f", key="s4l", disabled=h_lock)
    bias_4h_ok = st.checkbox("4H Confirmed", key="4h_c", disabled=h_lock or not (s4_h > 0 and s4_l > 0))

# 1H
with c1h:
    st.subheader("⏱️ 1H STRUC")
    itf_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", disabled=not bias_4h_ok)
    i_lock = not bias_4h_ok or itf_trend == "Select..."
    s1_h = st.number_input("High", value=0.0, format="%.2f", key="s1h", disabled=i_lock)
    s1_l = st.number_input("Low", value=0.0, format="%.2f", key="s1l", disabled=i_lock)
    bias_1h_ok = st.checkbox("1H Confirmed", key="1h_c", disabled=i_lock or not (s1_h > 0 and s1_l > 0))

# 30M
with c30m:
    st.subheader("⚡ 30M SHIFT")
    t30_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t", disabled=not bias_1h_ok)
    m30_lock = not bias_1h_ok or t30_trend == "Select..."
    s30_h = st.number_input("High", value=0.0, format="%.2f", key="s30h", disabled=m30_lock)
    s30_l = st.number_input("Low", value=0.0, format="%.2f", key="s30l", disabled=m30_lock)
    bias_30m_ok = st.checkbox("30M Confirmed", key="30m_c", disabled=m30_lock or not (s30_h > 0 and s30_l > 0))

# 15M
with c15m:
    st.subheader("🎯 15M ENTRY")
    t15_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t", disabled=not bias_30m_ok)
    m15_lock = not bias_30m_ok or t15_trend == "Select..."
    s15_h = st.number_input("High", value=0.0, format="%.2f", key="s15h", disabled=m15_lock)
    s15_l = st.number_input("Low", value=0.0, format="%.2f", key="s15l", disabled=m15_lock)
    bias_15m_ok = st.checkbox("15M Confirmed", key="15m_c", disabled=m15_lock or not (s15_h > 0 and s15_l > 0))

# ---------------- 5M MICRO-CONFIRMATION ---------------- #
st.markdown("---")
st.subheader("⚡ 5M MICRO-CONFIRMATION")
c5_1, c5_2, c5_3 = st.columns(3)

with c5_1:
    conf_type = st.radio("Confirmation Type", ["Waiting...", "MSS (Early Shift)", "BOS (Trend Continues)"], disabled=not bias_15m_ok)
with c5_2:
    fvg_present = st.checkbox("5M FVG / Displacement?", disabled=conf_type == "Waiting...")
with c5_3:
    trade_ready = st.checkbox("Price Returned to Zone?", disabled=not fvg_present)

if trade_ready:
    st.success(f"🔥 {conf_type} CONFIRMED: Ready to Execute.")

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
col_p2, col_p3 = st.columns([1, 2])

with col_p2:
    st.header("📋 PHASE 2: POI")
    poi = st.selectbox("Zone Type", ["Select...", "Swing High", "Swing Low", "Supply", "Demand", "FVG"], disabled=not trade_ready)
    entry_zone = st.number_input("Zone Price", value=0.0, format="%.2f", disabled=not trade_ready)

with col_p3:
    st.header("🚀 PHASE 3: EXECUTE")
    direction = st.radio("Position", ["LONG 🔵", "SHORT 🔴"], horizontal=True, disabled=not trade_ready)
    
    pip_val = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    
    sl_auto = entry_zone - (15 * pip_val) if direction == "LONG 🔵" else entry_zone + (15 * pip_val)
    
    sl = st.number_input("Stop Loss", value=sl_auto, format="%.2f", disabled=not trade_ready)
    entry = st.number_input("Entry Price", value=0.0, format="%.2f", disabled=not trade_ready)
    
    if entry > 0 and sl > 0:
        pips = abs(entry - sl) / pip_val
        lot = (current_risk_usd / pips) / 10 if pips > 0 else 0
        st.metric("Recommended Lot Size", f"{round(lot, 2)}")
        st.info(f"Risk: {round(pips, 1)} pips | Cash: ${round(current_risk_usd, 2)}")
