import streamlit as st
import re
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

st.title("🏹 BlackArrowFX: Triple-Timeframe Execution Engine")
st.caption(f"Current Server Time: {dt_string}")
st.markdown("---")

# ---------------- SESSION STATE ---------------- #
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11
if "trade_count" not in st.session_state:
    st.session_state.trade_count = 0
if "daily_loss_total" not in st.session_state:
    st.session_state.daily_loss_total = 0.0

# ---------------- SIDEBAR: RISK & JOURNAL ---------------- #
with st.sidebar:
    st.header("💰 Risk Engine")
    st.metric("Current Balance", f"${round(st.session_state.balance, 2)}")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 5.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0, step=0.0)

    max_daily_risk_limit = st.session_state.balance * 0.10
    st.info(f"Active Risk: ${round(current_risk_usd, 2)}")
    
    st.header("🌍 News Filter")
    st.markdown("[Check Forex Factory 📅](https://www.forexfactory.com/)")
    news_ok = st.toggle("No High Impact News")

    st.markdown("---")
    st.header("📊 Daily Journal")
    st.write(f"Trades Taken: **{st.session_state.trade_count} / 3**")
    
    loss_disabled = st.session_state.trade_count >= 3 or st.session_state.daily_loss_total >= max_daily_risk_limit
    if st.button("❌ RECORD LOSS", disabled=loss_disabled, use_container_width=True):
        st.session_state.balance -= current_risk_usd
        st.session_state.daily_loss_total += current_risk_usd
        st.session_state.trade_count += 1
        st.rerun()

    win_disabled = st.session_state.trade_count >= 3
    with st.expander("✅ RECORD WIN", expanded=not win_disabled):
        manual_profit = st.number_input("Profit Made ($)", min_value=0.0, value=current_risk_usd * 2, step=0.0)
        if st.button("Add to Balance", disabled=win_disabled):
            st.session_state.balance += manual_profit
            st.session_state.trade_count += 1
            st.rerun()

    if st.button("🔄 Reset Daily Limits"):
        st.session_state.trade_count = 0
        st.session_state.daily_loss_total = 0.0
        st.rerun()

# ---------------- SHARED PRICE INPUT ---------------- #
# We need a global market price to validate BOS/MSS automatically
st.header("📍 LIVE MARKET DATA")
curr_price = st.number_input("Enter Current XAUUSD Price", value=0.0, format="%.2f", step=0.0)
st.markdown("---")

# ---------------- TRIPLE TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c5m = st.columns(3)

# --- 4H BIAS ---
with c4h:
    st.subheader("⏳ 4H BIAS")
    htf_bias = st.radio("4H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", label_visibility="collapsed")
    s4_h = st.number_input("4H Swing High", value=0.0, format="%.2f", step=0.0, key="s4h")
    s4_l = st.number_input("4H Swing Low", value=0.0, format="%.2f", step=0.0, key="s4l")
    
    # Structural Logic for 4H
    can_confirm_4h = False
    if htf_bias == "Bullish ⬆️" and curr_price > s4_h and s4_h > 0: can_confirm_4h = True
    elif htf_bias == "Bearish ⬇️" and curr_price < s4_l and s4_l > 0: can_confirm_4h = True
    
    bias_4h_ok = st.checkbox("4H BOS Confirmed", disabled=not can_confirm_4h, key="c4h")
    if not can_confirm_4h and htf_bias != "Ranging":
        st.caption("⚠️ Price must break Swing level to confirm.")

# --- 1H STRUCTURE ---
with c1h:
    st.subheader("⏱️ 1H STRUCTURE")
    itf_trend = st.radio("1H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", label_visibility="collapsed")
    s1_h = st.number_input("1H Swing High", value=0.0, format="%.2f", step=0.0, key="s1h")
    s1_l = st.number_input("1H Swing Low", value=0.0, format="%.2f", step=0.0, key="s1l")
    
    # Structural Logic for 1H
    can_confirm_1h = False
    if itf_trend == "Bullish ⬆️" and curr_price > s1_h and s1_h > 0: can_confirm_1h = True
    elif itf_trend == "Bearish ⬇️" and curr_price < s1_l and s1_l > 0: can_confirm_1h = True
    
    bias_1h_ok = st.checkbox("1H Structure Confirmed", disabled=not can_confirm_1h, key="c1h")

# --- 5M SHIFT ---
with c5m:
    st.subheader("⚡ 5M SHIFT")
    ltf_trend = st.radio("5M Shift", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="5m_t", label_visibility="collapsed")
    s5_h = st.number_input("5M Swing High", value=0.0, format="%.2f", step=0.0, key="s5h")
    s5_l = st.number_input("5M Swing Low", value=0.0, format="%.2f", step=0.0, key="s5l")
    
    # Structural Logic for 5M (MSS)
    can_confirm_5m = False
    if ltf_trend == "Bullish ⬆️" and curr_price > s5_h and s5_h > 0: can_confirm_5m = True
    elif ltf_trend == "Bearish ⬇️" and curr_price < s5_l and s5_l > 0: can_confirm_5m = True
    
    bias_5m_ok = st.checkbox("5M MSS Confirmed", disabled=not can_confirm_5m, key="c5h")

# Final Logic Check
all_phases_ready = bias_4h_ok and bias_1h_ok and bias_5m_ok

# ---------------- POI & EXECUTION ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 POI PLAN")
    raw_text = st.text_area("Paste 1H POI Zones", height=100, placeholder="Example: 1H Demand $2340 - $2345")
    POI_DB = {}
    if raw_text:
        lines = raw_text.split("\n")
        for line in lines:
            line = line.strip().replace("–", "-")
            match = re.search(r"(\d{3,5}\.?\d*)\s*-\s*(\d{3,5}\.?\d*)", line)
            if match:
                low, high = float(match.group(1)), float(match.group(2))
                name = line.split("$")[0].strip() or f"Zone {len(POI_DB)+1}"
                POI_DB[name] = {"low": low, "high": high}

    inside_zone = False
    if POI_DB:
        selected_poi = st.selectbox("Active POI", list(POI_DB.keys()))
        target = POI_DB[selected_poi]
        if target["low"] <= curr_price <= target["high"]:
            st.success("✅ AT POI")
            inside_zone = True
        else:
            st.error("❌ OUTSIDE POI")

with col_exec:
    st.header("🚀 EXECUTION ENGINE")
    calc_c1, calc_c2 = st.columns(2)
    with calc_c1:
        entry = st.number_input("Entry Price", value=0.0, format="%.2f", step=0.0)
        sl = st.number_input("Stop Loss", value=0.0, format="%.2f", step=0.0)
    
    with calc_c2:
        if entry > 0 and sl > 0:
            pips = abs(entry - sl) * 10
            lot = current_risk_usd / (pips * 10) if pips > 0 else 0
            st.metric("Lot Size", round(lot, 2))
            
            if all_phases_ready and inside_zone and news_ok:
                st.success("🔥 ALL LEVELS CONFIRMED: EXECUTE")
            else:
                st.error("🚫 DO NOT ENTER: Check Structural Breaks")

    if entry > 0 and sl > 0:
        diff = abs(entry - sl)
        is_buy = entry > sl
        st.write(f"TP1 (1.5R): **{round(entry + (diff * 1.5 if is_buy else -diff * 1.5), 2)}** | TP2 (3.0R): **{round(entry + (diff * 3.0 if is_buy else -diff * 3.0), 2)}**")
