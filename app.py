import streamlit as st
from datetime import datetime

# ---------------- SETUP & THEME ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & SYSTEM ---------------- #
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
    news_ok = st.toggle("No High Impact News", value=False)
    
    if not news_ok:
        st.error("🚨 SYSTEM LOCKED: News must be cleared.")

    if "trade_count" not in st.session_state: st.session_state.trade_count = 0

    st.header("📊 Daily Journal")
    journal_disabled = not news_ok or st.session_state.trade_count >= 3
    col_loss, col_win = st.columns(2)
    with col_loss:
        if st.button("❌ LOSS", disabled=journal_disabled, use_container_width=True):
            st.session_state.balance -= current_risk_usd
            st.session_state.trade_count += 1
            st.rerun()
    with col_win:
        if st.button("✅ WIN", disabled=journal_disabled, use_container_width=True):
            st.session_state.balance += (current_risk_usd * 2) 
            st.session_state.trade_count += 1
            st.rerun()

# ---------------- MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Asset: {symbol} | Mode: {asset_type} | Server Time: {dt_string}")
st.markdown("---")

# ---------------- QUAD TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)

# --- 4H BIAS ---
with c4h:
    st.subheader("⏳ 4H BIAS")
    htf_bias = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", disabled=not news_ok)
    h_lock = not news_ok or htf_bias == "Select..."
    s4_h = st.number_input("Swing High", value=0.0, format="%.2f", key="s4h", disabled=h_lock)
    s4_l = st.number_input("Swing Low", value=0.0, format="%.2f", key="s4l", disabled=h_lock)
    bias_4h_ok = st.checkbox("4H Confirmed", key="4h_c", disabled=h_lock or not (s4_h > 0 and s4_l > 0))

# --- 1H STRUC ---
with c1h:
    st.subheader("⏱️ 1H STRUC")
    itf_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", disabled=not bias_4h_ok)
    i_lock = not bias_4h_ok or itf_trend == "Select..."
    s1_h = st.number_input("Swing High", value=0.0, format="%.2f", key="s1h", disabled=i_lock)
    s1_l = st.number_input("Swing Low", value=0.0, format="%.2f", key="s1l", disabled=i_lock)
    bias_1h_ok = st.checkbox("1H Confirmed", key="1h_c", disabled=i_lock or not (s1_h > 0 and s1_l > 0))

# --- 30M SHIFT ---
with c30m:
    st.subheader("⚡ 30M SHIFT")
    t30_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t", disabled=not bias_1h_ok)
    m30_lock = not bias_1h_ok or t30_trend == "Select..."
    s30_h = st.number_input("Swing High", value=0.0, format="%.2f", key="s30h", disabled=m30_lock)
    s30_l = st.number_input("Swing Low", value=0.0, format="%.2f", key="s30l", disabled=m30_lock)
    bias_30m_ok = st.checkbox("30M Confirmed", key="30m_c", disabled=m30_lock or not (s30_h > 0 and s30_l > 0))

# --- 15M ENTRY ---
with c15m:
    st.subheader("🎯 15M ENTRY")
    t15_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t", disabled=not bias_30m_ok)
    m15_lock = not bias_30m_ok or t15_trend == "Select..."
    s15_h = st.number_input("Swing High", value=0.0, format="%.2f", key="s15h", disabled=m15_lock)
    s15_l = st.number_input("Swing Low", value=0.0, format="%.2f", key="s15l", disabled=m15_lock)
    bias_15m_ok = st.checkbox("15M Confirmed", key="15m_c", disabled=m15_lock or not (s15_h > 0 and s15_l > 0))

# ---------------- 5M MICRO-CONFIRMATION ---------------- #
st.markdown("---")
st.subheader("⚡ 5M MICRO-CONFIRMATION (Trigger)")
c5_1, c5_2, c5_3 = st.columns(3)

with c5_1:
    m5_mss = st.checkbox("5M Market Structure Shift (MSS)?", key="m5mss", disabled=not bias_15m_ok)
with c5_2:
    m5_fvg = st.checkbox("5M FVG / Displacement Found?", key="m5fvg", disabled=not m5_mss)
with c5_3:
    trade_trigger = st.checkbox("5M Price Returned to Zone?", key="m5trig", disabled=not m5_fvg)

if trade_trigger:
    st.success("🎯 5M ALIGNMENT COMPLETE: Prepare for Execution.")
else:
    st.info("⏳ Waiting for 5M MSS + FVG + Return to Zone to unlock Phase 3.")

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
ready_to_trade = trade_trigger and news_ok

col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Where am I trading?", ["Select...", "Swing High", "Swing Low", "Supply Zone", "Demand Zone", "Order Block", "FVG"], disabled=not ready_to_trade)
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f", disabled=not ready_to_trade)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    trade_dir = st.radio("Trade Direction", ["LONG 🔵", "SHORT 🔴"], horizontal=True, disabled=not ready_to_trade)
    
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    
    # Auto SL Logic (15 pips)
    calc_sl = 0.0
    if zone_price > 0:
        calc_sl = zone_price - (15 * pip_factor) if trade_dir == "LONG 🔵" else zone_price + (15 * pip_factor)

    sl = st.number_input("Stop Loss", value=calc_sl, format="%.2f", disabled=not ready_to_trade)
    entry = st.number_input("Manual Entry Price", value=0.0, format="%.2f", disabled=not ready_to_trade)
    
    if entry > 0 and sl > 0:
        pips_diff = abs(entry - sl) / pip_factor
        if pips_diff > 0:
            lot = (current_risk_usd / pips_diff) / 10
            st.metric("Calculated Lot Size", f"{round(lot, 2)}")
            st.write(f"📏 Distance: {round(pips_diff, 1)} pips | 💵 Risk: ${round(current_risk_usd, 2)}")
